"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { ModulePage } from "@/components/shared/ModulePage";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "@/components/ui/toast";
import { apiRequest } from "@/lib/api";
import { MODULE_DESCRIPTIONS } from "@/lib/navigation";
import { formatRelativeTime } from "@/lib/utils";

export default function CommunityPage() {
  const qc = useQueryClient();
  const { data: posts, isLoading: postsLoading } = useQuery({ queryKey: ["community-posts"], queryFn: () => apiRequest<{ results: any[] }>("/community/posts/", { method: "GET" }) });
  const { data: announcements, isLoading: annLoading } = useQuery({ queryKey: ["community-announcements"], queryFn: () => apiRequest<{ results: any[] }>("/community/announcements/", { method: "GET" }) });
  const { data: polls, isLoading: pollsLoading } = useQuery({ queryKey: ["community-polls"], queryFn: () => apiRequest<{ results: any[] }>("/community/polls/", { method: "GET" }) });
  const { data: lostFound, isLoading: lfLoading } = useQuery({ queryKey: ["community-lostfound"], queryFn: () => apiRequest<{ results: any[] }>("/community/lost-found/", { method: "GET" }) });

  const [postForm, setPostForm] = useState({ title: "", body: "", category: "general" });
  const postMutation = useMutation({
    mutationFn: (data: typeof postForm) => apiRequest("/community/posts/", { method: "POST", body: data }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["community-posts"] }); setPostForm({ title: "", body: "", category: "general" }); toast.success("Post published."); },
    onError: (e: Error) => toast.error(e.message),
  });

  const pinV: Record<string,any> = { normal:"secondary", high:"warning", urgent:"destructive" };
  const lfV: Record<string,any> = { lost:"destructive", found:"success" };

  return (
    <ModulePage title="Community" description={MODULE_DESCRIPTIONS.community} iconKey="community" badge="Active">
      <Tabs defaultValue="announcements" className="space-y-4">
        <TabsList><TabsTrigger value="announcements">Announcements</TabsTrigger><TabsTrigger value="posts">Posts</TabsTrigger><TabsTrigger value="polls">Polls</TabsTrigger><TabsTrigger value="lostfound">Lost &amp; Found</TabsTrigger></TabsList>

        <TabsContent value="announcements">
          <div className="space-y-4">
            {annLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (announcements?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No announcements.</p> :
              (announcements?.results ?? []).map((a: any) => (
                <Card key={a.id}><CardHeader><div className="flex items-start justify-between"><CardTitle className="text-base">{a.title}</CardTitle><Badge variant={pinV[a.priority] ?? "secondary"} className="capitalize">{a.priority}</Badge></div><CardDescription>{formatRelativeTime(a.created_at)}</CardDescription></CardHeader>
                <CardContent><p className="text-sm whitespace-pre-line">{a.body}</p></CardContent></Card>))}
          </div>
        </TabsContent>

        <TabsContent value="posts" className="space-y-4">
          <Card><CardHeader><CardTitle>New post</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-1"><Label>Title</Label><Input value={postForm.title} onChange={e => setPostForm(p => ({...p, title: e.target.value}))} placeholder="What's on your mind?" /></div>
            <div className="space-y-1"><Label>Body</Label><Textarea value={postForm.body} onChange={e => setPostForm(p => ({...p, body: e.target.value}))} /></div>
            <Button disabled={postMutation.isPending || !postForm.title} onClick={() => postMutation.mutate(postForm)}>{postMutation.isPending ? "Publishing..." : "Publish"}</Button>
          </CardContent></Card>
          <div className="space-y-4">
            {postsLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (posts?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No posts yet.</p> :
              (posts?.results ?? []).map((p: any) => (
                <Card key={p.id}><CardHeader><CardTitle className="text-base">{p.title}</CardTitle><CardDescription>{formatRelativeTime(p.created_at)} · {p.like_count ?? 0} likes · {p.comment_count ?? 0} comments</CardDescription></CardHeader>
                <CardContent><p className="text-sm line-clamp-3">{p.body}</p></CardContent></Card>))}
          </div>
        </TabsContent>

        <TabsContent value="polls">
          <div className="space-y-4">
            {pollsLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (polls?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No active polls.</p> :
              (polls?.results ?? []).map((p: any) => (
                <Card key={p.id}><CardHeader><CardTitle className="text-base">{p.question}</CardTitle><CardDescription><Badge variant={p.status === "active" ? "success" : "secondary"} className="capitalize">{p.status}</Badge></CardDescription></CardHeader>
                <CardContent><p className="text-sm text-muted-foreground">{(p.options ?? []).length} options · Ends {p.end_date ? new Date(p.end_date).toLocaleDateString() : "—"}</p></CardContent></Card>))}
          </div>
        </TabsContent>

        <TabsContent value="lostfound">
          <Card><CardHeader><CardTitle>Lost &amp; Found board</CardTitle><CardDescription>Items reported lost or found within the estate.</CardDescription></CardHeader>
          <CardContent>{lfLoading ? <p className="text-sm text-muted-foreground">Loading...</p> : (lostFound?.results ?? []).length === 0 ? <p className="text-sm text-muted-foreground">No items reported.</p> : (
            <Table><TableHeader><TableRow><TableHead>Type</TableHead><TableHead>Item</TableHead><TableHead>Location</TableHead><TableHead>Status</TableHead><TableHead>When</TableHead></TableRow></TableHeader>
            <TableBody>{(lostFound?.results ?? []).map((i: any) => (<TableRow key={i.id}><TableCell><Badge variant={lfV[i.item_type] ?? "secondary"} className="capitalize">{i.item_type}</Badge></TableCell><TableCell className="font-medium">{i.title}</TableCell><TableCell>{i.location || "—"}</TableCell><TableCell><Badge variant={i.status === "resolved" ? "success" : "secondary"} className="capitalize">{i.status}</Badge></TableCell><TableCell>{formatRelativeTime(i.created_at)}</TableCell></TableRow>))}</TableBody></Table>)}
          </CardContent></Card>
        </TabsContent>
      </Tabs>
    </ModulePage>
  );
}
