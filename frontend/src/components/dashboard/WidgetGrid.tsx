"use client";

import { motion } from "framer-motion";

interface WidgetGridProps {
  children: React.ReactNode;
  className?: string;
}

export function WidgetGrid({ children, className }: WidgetGridProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={className ?? "grid gap-4 sm:grid-cols-2 xl:grid-cols-4"}
    >
      {children}
    </motion.div>
  );
}
