"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BookOpen,
  BrainCircuit,
  LayoutDashboard,
  MessageSquare,
  Settings,
  Ticket,
  Workflow,
} from "lucide-react";
const links = [
  ["/", "Dashboard", LayoutDashboard],
  ["/chat", "AI Chat", MessageSquare],
  ["/knowledge", "Knowledge Base", BookOpen],
  ["/tickets", "Tickets", Ticket],
  ["/classifier", "AI Classifier", BrainCircuit],
  ["/automation", "Automation", Workflow],
  ["/status", "System Status", Activity],
  ["/settings", "Settings", Settings],
] as const;
export function AppShell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  return (
    <div className="shell">
      <aside>
        <div className="brand">
          <span className="logo">AI</span>
          <div>
            Support Hub<small>Intelligent helpdesk</small>
          </div>
        </div>
        <nav>
          {links.map(([href, label, Icon]) => (
            <Link
              href={href}
              key={href}
              className={path === href ? "active" : ""}
            >
              <Icon size={18} />
              <span>{label}</span>
            </Link>
          ))}
        </nav>
        <div className="sidebar-foot">
          <span className="dot" /> Mock mode ready
        </div>
      </aside>
      <main>
        <header>
          <div>
            <h1>{links.find((x) => x[0] === path)?.[1] || "AI Support Hub"}</h1>
            <p>Intelligent RAG Helpdesk & AI Automation</p>
          </div>
          <span className="env">Development</span>
        </header>
        <section className="content">{children}</section>
      </main>
    </div>
  );
}
