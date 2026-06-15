"""RAG document embedding and retrieval tests with mocks."""
from unittest.mock import MagicMock

import pytest

from ai.models import Document, Embedding
from ai.rag import chunk_text, cosine_similarity, embed_chunks, retrieve_relevant_chunks


def mock_embed_fn(text: str) -> list[float]:
    """Deterministic mock embedding based on text hash."""
    base = sum(ord(c) for c in text) % 100 / 100.0
    return [base, 1.0 - base, 0.5]


@pytest.mark.django_db
class TestDocumentChunking:
    def test_chunk_empty_text(self):
        assert chunk_text("") == []

    def test_chunk_short_text(self):
        text = "Estate gate hours are 6 AM to 10 PM."
        chunks = chunk_text(text, chunk_size=512)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_long_text_with_overlap(self):
        text = "A" * 1000
        chunks = chunk_text(text, chunk_size=400, overlap=50)
        assert len(chunks) >= 2
        assert all(len(c) <= 400 for c in chunks)


@pytest.mark.django_db
class TestEmbedding:
    def test_embed_chunks_with_mock(self):
        chunks = ["Gate policy document", "Visitor pass rules"]
        results = embed_chunks(chunks, embed_fn=mock_embed_fn)
        assert len(results) == 2
        assert all(len(r["embedding_vector"]) == 3 for r in results)
        assert results[0]["chunk_index"] == 0

    def test_cosine_similarity_identical_vectors(self):
        vector = [0.5, 0.5, 0.5]
        assert cosine_similarity(vector, vector) == pytest.approx(1.0, abs=0.01)

    def test_cosine_similarity_orthogonal_vectors(self):
        assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0, abs=0.01)

    def test_retrieve_relevant_chunks(self):
        embeddings = [
            {"chunk_text": "Pool hours", "embedding_vector": [0.9, 0.1, 0.5]},
            {"chunk_text": "Gate policy", "embedding_vector": [0.1, 0.9, 0.5]},
            {"chunk_text": "Parking rules", "embedding_vector": [0.5, 0.5, 0.5]},
        ]
        query = [0.85, 0.15, 0.5]
        results = retrieve_relevant_chunks(query, embeddings, top_k=2)
        assert len(results) == 2
        assert results[0]["chunk_text"] == "Pool hours"


@pytest.mark.django_db
class TestDocumentModelIntegration:
    def test_document_indexing_workflow(self, estate, admin_user):
        doc = Document.objects.create(
            estate=estate,
            title="Estate FAQ",
            document_type=Document.DocumentType.FAQ,
            content_text="Visitors must register at the gate. Pool opens at 8 AM.",
            uploaded_by=admin_user,
        )
        chunks = chunk_text(doc.content_text, chunk_size=40)
        embedded = embed_chunks(chunks, embed_fn=mock_embed_fn)

        Embedding.objects.bulk_create(
            [
                Embedding(
                    estate=estate,
                    document=doc,
                    chunk_index=item["chunk_index"],
                    chunk_text=item["chunk_text"],
                    embedding_vector=item["embedding_vector"],
                    model_name=item["model_name"],
                )
                for item in embedded
            ]
        )

        doc.status = Document.Status.INDEXED
        doc.chunk_count = len(embedded)
        doc.save(update_fields=["status", "chunk_count", "updated_at"])

        doc.refresh_from_db()
        assert doc.status == Document.Status.INDEXED
        assert doc.embeddings.count() == doc.chunk_count

    def test_mock_openai_embed_client(self):
        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=[0.1, 0.2, 0.3])]
        )

        def openai_embed(text):
            response = mock_client.embeddings.create(input=text, model="text-embedding-3-small")
            return response.data[0].embedding

        result = embed_chunks(["test query"], embed_fn=openai_embed)
        assert result[0]["embedding_vector"] == [0.1, 0.2, 0.3]
        mock_client.embeddings.create.assert_called_once()
