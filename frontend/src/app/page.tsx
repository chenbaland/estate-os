"use client";

import { motion } from "framer-motion";
import {
  ArrowRight,
  Building2,
  Shield,
  Sparkles,
  Star,
  Users,
  Zap,
} from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useTheme } from "@/hooks/useTheme";

const features = [
  {
    icon: Shield,
    title: "Enterprise Security",
    description:
      "Visitor management, patrol logs, SOS alerts, and real-time gate access control.",
  },
  {
    icon: Zap,
    title: "Smart Utilities",
    description:
      "Monitor consumption, purchase tokens, and automate billing across your estate.",
  },
  {
    icon: Users,
    title: "Resident Experience",
    description:
      "Self-service portal for bills, packages, facilities, and community engagement.",
  },
  {
    icon: Sparkles,
    title: "AI Concierge",
    description:
      "Intelligent assistant for residents and staff — answers, bookings, and insights.",
  },
];

const stats = [
  { value: "50K+", label: "Residents managed" },
  { value: "200+", label: "Estates onboarded" },
  { value: "99.9%", label: "Platform uptime" },
  { value: "4.9", label: "Resident satisfaction", icon: Star },
];

export default function LandingPage() {
  const { mounted, isDark } = useTheme();

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b glass">
        <div className="container-app flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg gradient-brand text-sm font-bold text-white">
              E
            </div>
            <span className="text-lg font-semibold tracking-tight">EstateOS</span>
          </Link>
          <nav className="hidden items-center gap-6 md:flex" aria-label="Site">
            <a href="#features" className="text-sm text-muted-foreground hover:text-foreground">
              Features
            </a>
            <a href="#stats" className="text-sm text-muted-foreground hover:text-foreground">
              Platform
            </a>
          </nav>
          <div className="flex items-center gap-2">
            <Button variant="ghost" asChild>
              <Link href="/login">Sign in</Link>
            </Button>
            <Button asChild>
              <Link href="/register">Get started</Link>
            </Button>
          </div>
        </div>
      </header>

      <section className="relative overflow-hidden">
        <div
          className={`absolute inset-0 -z-10 ${
            mounted && isDark
              ? "bg-[radial-gradient(ellipse_at_top,hsl(262_83%_20%/0.4),transparent_50%)]"
              : "bg-[radial-gradient(ellipse_at_top,hsl(262_83%_90%/0.5),transparent_50%)]"
          }`}
        />
        <div className="container-app py-24 md:py-32">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mx-auto max-w-3xl text-center"
          >
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border bg-background/80 px-4 py-1.5 text-sm backdrop-blur">
              <Building2 className="h-4 w-4 text-primary" />
              The operating system for modern estates
            </div>
            <h1 className="text-balance text-4xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
              Premium living,{" "}
              <span className="bg-gradient-to-r from-primary to-blue-500 bg-clip-text text-transparent">
                intelligently managed
              </span>
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground sm:text-xl">
              EstateOS unifies security, billing, utilities, healthcare, and community
              — inspired by the best of Airbnb hospitality and Revolut simplicity.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button size="lg" className="h-12 px-8 text-base" asChild>
                <Link href="/register">
                  Start free trial
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="h-12 px-8 text-base" asChild>
                <Link href="/login">Sign in to dashboard</Link>
              </Button>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="relative mx-auto mt-16 max-w-5xl"
          >
            <div className="rounded-2xl border bg-card p-2 shadow-2xl">
              <div className="overflow-hidden rounded-xl bg-muted/50">
                <div className="flex items-center gap-2 border-b bg-card px-4 py-3">
                  <div className="flex gap-1.5">
                    <span className="h-3 w-3 rounded-full bg-red-400" />
                    <span className="h-3 w-3 rounded-full bg-yellow-400" />
                    <span className="h-3 w-3 rounded-full bg-green-400" />
                  </div>
                  <span className="text-xs text-muted-foreground">EstateOS Dashboard</span>
                </div>
                <div className="grid gap-4 p-6 md:grid-cols-3">
                  {["Occupancy", "Revenue", "Open Tickets"].map((label, i) => (
                    <Card key={label} className="border-0 shadow-sm">
                      <CardContent className="p-4">
                        <p className="text-sm text-muted-foreground">{label}</p>
                        <p className="mt-1 text-2xl font-bold">
                          {["94%", "₦12.4M", "23"][i]}
                        </p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <section id="stats" className="border-y bg-muted/30 py-16">
        <div className="container-app">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            {stats.map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center"
              >
                <p className="flex items-center justify-center gap-1 text-3xl font-bold md:text-4xl">
                  {stat.value}
                  {stat.icon && <Star className="h-5 w-5 fill-warning text-warning" />}
                </p>
                <p className="mt-1 text-sm text-muted-foreground">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section id="features" className="py-24">
        <div className="container-app">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Everything your estate needs
            </h2>
            <p className="mt-4 text-muted-foreground">
              One platform for administrators, residents, security, and service providers.
            </p>
          </div>
          <div className="mt-16 grid gap-6 md:grid-cols-2">
            {features.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                >
                  <Card className="h-full border-0 bg-muted/30 transition-shadow hover:shadow-lg">
                    <CardContent className="flex gap-4 p-6">
                      <div className="rounded-xl bg-primary/10 p-3 text-primary">
                        <Icon className="h-6 w-6" />
                      </div>
                      <div>
                        <h3 className="font-semibold">{feature.title}</h3>
                        <p className="mt-2 text-sm text-muted-foreground">
                          {feature.description}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="border-t bg-primary py-20 text-primary-foreground">
        <div className="container-app text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Ready to transform your estate?
          </h2>
          <p className="mx-auto mt-4 max-w-xl opacity-90">
            Join leading property managers who trust EstateOS for secure, seamless operations.
          </p>
          <Button
            size="lg"
            variant="secondary"
            className="mt-8 h-12 px-8"
            asChild
          >
            <Link href="/register">Create your account</Link>
          </Button>
        </div>
      </section>

      <footer className="border-t py-8">
        <div className="container-app flex flex-col items-center justify-between gap-4 sm:flex-row">
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} EstateOS. All rights reserved.
          </p>
          <div className="flex gap-6 text-sm text-muted-foreground">
            <Link href="/login" className="hover:text-foreground">
              Sign in
            </Link>
            <Link href="/register" className="hover:text-foreground">
              Register
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
