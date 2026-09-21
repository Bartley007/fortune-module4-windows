"use client";

import {
  BookOpen,
  Bot,
  ExternalLink,
  FileText,
  Library,
  MessageSquarePlus,
  NotebookPen,
  Plus,
  Send,
  Sparkles,
  Tags,
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import type { CollectionItem, NoteItem, TagItem } from "@/lib/types";

interface AgentSource {
  id: string;
  kind: "collection" | "note";
  title: string;
  sourceId: string | null;
  excerpt: string;
  url: string | null;
  tags: string[];
}

interface AgentMessage {
  id: string;
  role: "agent" | "user";
  content: string;
  sources: AgentSource[];
}

interface KnowledgeAgentProps {
  collections: CollectionItem[];
  notes: NoteItem[];
  tags: TagItem[];
  userId: string;
  loading: boolean;
  onAddCollection: () => void;
  onAddNote: () => void;
}

const quickPrompts = [
  "概览我的个人知识库",
  "找出与体用有关的记录",
  "汇总我的个人笔记",
  "哪些内容带有复习标签",
];

function createMessageId(role: AgentMessage["role"]): string {
  return `${role}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function compactText(value: string, max = 150): string {
  const normalized = value.replace(/\s+/g, " ").trim();
  return normalized.length > max ? `${normalized.slice(0, max)}…` : normalized;
}

function sourceUrl(item: CollectionItem): string | null {
  const value = item.source_metadata?.url;
  return typeof value === "string" && value.trim() ? value : null;
}

function toCollectionSource(item: CollectionItem): AgentSource {
  const metadataSummary = item.source_metadata?.summary;
  return {
    id: item.collection_id,
    kind: "collection",
    title: item.title || item.source_id || "未命名收藏",
    sourceId: item.source_id,
    excerpt:
      typeof metadataSummary === "string"
        ? compactText(metadataSummary)
        : `${item.item_type} · 收藏于知识库`,
    url: sourceUrl(item),
    tags: [],
  };
}

function toNoteSource(note: NoteItem): AgentSource {
  return {
    id: note.note_id,
    kind: "note",
    title: note.title || "未命名笔记",
    sourceId: note.source_id,
    excerpt: compactText(note.body),
    url: null,
    tags: note.tags,
  };
}

function queryTerms(query: string): string[] {
  const normalized = query.toLowerCase().replace(/\s+/g, "");
  const terms = new Set<string>();
  if (normalized.length > 1) terms.add(normalized);

  for (const chunk of normalized.split(/[，。！？、,.!?;；:：]+/)) {
    if (chunk.length > 1) terms.add(chunk);
  }

  const hanCharacters = Array.from(normalized).filter((value) => /[\u3400-\u9fff]/.test(value));
  for (let index = 0; index < hanCharacters.length - 1; index += 1) {
    terms.add(`${hanCharacters[index]}${hanCharacters[index + 1]}`);
  }
  return [...terms];
}

function scoreSource(source: AgentSource, terms: string[]): number {
  const fields = [
    { value: source.title, weight: 8 },
    { value: source.sourceId || "", weight: 6 },
    { value: source.tags.join(" "), weight: 5 },
    { value: source.excerpt, weight: 2 },
  ];
  let score = 0;
  for (const term of terms) {
    for (const field of fields) {
      if (field.value.toLowerCase().includes(term)) {
        score += field.weight;
      }
    }
  }
  return score;
}

function buildLocalAnswer(query: string, sources: AgentSource[]): string {
  const lowered = query.toLowerCase();
  const collectionCount = sources.filter((item) => item.kind === "collection").length;
  const noteCount = sources.filter((item) => item.kind === "note").length;
  const summaryIntent = ["概览", "总结", "统计", "多少", "全部", "所有"].some((keyword) =>
    lowered.includes(keyword),
  );

  if (summaryIntent) {
    const lines = [
      `当前资料中有 ${collectionCount} 个收藏来源和 ${noteCount} 条个人笔记。`,
    ];
    if (sources.length) {
      lines.push("", "最近可检索的内容：");
      sources.slice(0, 3).forEach((item, index) => {
        lines.push(`${index + 1}. ${item.title}${item.sourceId ? ` · ${item.sourceId}` : ""}`);
      });
    }
    return lines.join("\n");
  }

  if (!sources.length) {
    return [
      "我在当前个人知识库中没有找到与这个问题直接相关的记录。",
      "",
      "你可以换一个关键词，或者先把典籍段落、卦象签文和相关笔记收藏进来。",
    ].join("\n");
  }

  const lines = [`我找到了 ${sources.length} 条可能相关的个人资料：`];
  sources.slice(0, 3).forEach((item, index) => {
    lines.push(
      "",
      `${index + 1}. ${item.title}`,
      item.sourceId ? `来源标识：${item.sourceId}` : "来源标识：个人笔记",
      item.excerpt,
    );
  });
  lines.push("", "以上结果来自你的收藏和笔记，不包含知识库之外的推断。");
  return lines.join("\n");
}

export default function KnowledgeAgent({
  collections,
  notes,
  tags,
  userId,
  loading,
  onAddCollection,
  onAddNote,
}: KnowledgeAgentProps) {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [thinking, setThinking] = useState(false);
  const transcriptRef = useRef<HTMLDivElement>(null);

  const allSources = useMemo(
    () => [
      ...collections.map(toCollectionSource),
      ...notes.map(toNoteSource),
    ],
    [collections, notes],
  );

  useEffect(() => {
    const stored = window.localStorage.getItem(`module4-agent-${userId}`);
    if (stored) {
      try {
        setMessages(JSON.parse(stored) as AgentMessage[]);
        return;
      } catch {
        window.localStorage.removeItem(`module4-agent-${userId}`);
      }
    }

    setMessages([
      {
        id: createMessageId("agent"),
        role: "agent",
        content: [
          "我是你的个人知识库智能体。",
          "你可以直接询问收藏内容、典籍来源、个人笔记或标签。我会先检索你的私有资料，再给出带来源标识的回答。",
        ].join("\n"),
        sources: [],
      },
    ]);
  }, [userId]);

  useEffect(() => {
    if (messages.length) {
      window.localStorage.setItem(`module4-agent-${userId}`, JSON.stringify(messages));
    }
  }, [messages, userId]);

  useEffect(() => {
    transcriptRef.current?.scrollTo({
      top: transcriptRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, thinking]);

  function answer(query: string) {
    const lowered = query.toLowerCase();
    const terms = queryTerms(query);
    let candidates = allSources
      .map((source) => ({ source, score: scoreSource(source, terms) }))
      .filter((item) => item.score > 0)
      .sort((left, right) => right.score - left.score)
      .map((item) => item.source);

    const summaryIntent = ["概览", "总结", "统计", "多少", "全部", "所有"].some((keyword) =>
      lowered.includes(keyword),
    );
    if (summaryIntent && !candidates.length) {
      candidates = allSources.slice(0, 6);
    }

    const response: AgentMessage = {
      id: createMessageId("agent"),
      role: "agent",
      content: buildLocalAnswer(query, candidates),
      sources: candidates.slice(0, 4),
    };
    window.setTimeout(() => {
      setMessages((current) => [...current, response]);
      setThinking(false);
    }, 260);
  }

  function sendMessage(rawQuery: string) {
    const query = rawQuery.trim();
    if (!query || thinking) return;

    setMessages((current) => [
      ...current,
      {
        id: createMessageId("user"),
        role: "user",
        content: query,
        sources: [],
      },
    ]);
    setDraft("");
    setThinking(true);
    answer(query);
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    sendMessage(draft);
  }

  function resetConversation() {
    const initial: AgentMessage[] = [
      {
        id: createMessageId("agent"),
        role: "agent",
        content: "已开始新的对话。你可以继续询问收藏内容、来源或个人笔记。",
        sources: [],
      },
    ];
    setMessages(initial);
    setDraft("");
  }

  return (
    <section className="page-shell agent-shell" id="agent">
      <div className="agent-card">
        <header className="agent-header">
          <span className="agent-mark"><Bot size={22} /></span>
          <div>
            <p className="kicker">PERSONAL KNOWLEDGE AGENT</p>
            <h2>藏书问答智能体</h2>
          </div>
          <div className="agent-state">
            <span className={loading ? "status-dot offline" : "status-dot"} />
            <span>{loading ? "正在读取个人资料" : `${allSources.length} 条资料可检索`}</span>
          </div>
          <button
            aria-label="开始新对话"
            onClick={resetConversation}
            title="开始新对话"
            type="button"
          >
            <MessageSquarePlus size={17} />
          </button>
        </header>

        <div className="agent-transcript" ref={transcriptRef}>
          {messages.map((message) => (
            <article className={`agent-message ${message.role}`} key={message.id}>
              <span className="message-avatar">
                {message.role === "agent" ? <Sparkles size={15} /> : "我"}
              </span>
              <div className="message-content">
                <div className="message-bubble">
                  {message.content.split("\n").map((line, index) => (
                    <p key={`${message.id}-${index}`}>{line || "\u00a0"}</p>
                  ))}
                </div>
                {message.sources.length ? (
                  <div className="agent-sources">
                    {message.sources.map((source) => (
                      <div className="agent-source" key={`${message.id}-${source.id}`}>
                        <span className="source-kind">
                          {source.kind === "collection" ? <Library size={14} /> : <NotebookPen size={14} />}
                        </span>
                        <div>
                          <strong>{source.title}</strong>
                          <small>{source.sourceId || "个人笔记"}</small>
                        </div>
                        {source.url ? (
                          <a href={source.url} rel="noreferrer" target="_blank">
                            <ExternalLink size={14} />
                          </a>
                        ) : null}
                      </div>
                    ))}
                  </div>
                ) : null}
              </div>
            </article>
          ))}
          {thinking ? (
            <article className="agent-message agent">
              <span className="message-avatar"><Sparkles size={15} /></span>
              <div className="message-bubble thinking-bubble">
                <span />
                <span />
                <span />
              </div>
            </article>
          ) : null}
        </div>

        <div className="quick-prompts">
          {quickPrompts.map((prompt) => (
            <button key={prompt} onClick={() => sendMessage(prompt)} type="button">
              {prompt}
            </button>
          ))}
        </div>

        <form className="agent-composer" onSubmit={submit}>
          <label>
            <span className="sr-only">向个人知识库提问</span>
            <textarea
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  sendMessage(draft);
                }
              }}
              placeholder="询问你的收藏、典籍来源、笔记或标签……"
              rows={2}
              value={draft}
            />
          </label>
          <button aria-label="发送问题" disabled={!draft.trim() || thinking} title="发送" type="submit">
            <Send size={18} />
          </button>
        </form>
      </div>

      <aside className="agent-context">
        <section>
          <p className="kicker">LIBRARY SNAPSHOT</p>
          <h3>你的知识库</h3>
          <div className="agent-stats">
            <div><BookOpen size={16} /><strong>{collections.length}</strong><span>收藏</span></div>
            <div><NotebookPen size={16} /><strong>{notes.length}</strong><span>笔记</span></div>
            <div><Tags size={16} /><strong>{tags.length}</strong><span>标签</span></div>
          </div>
        </section>
        <section className="agent-actions">
          <p className="kicker">QUICK ACTIONS</p>
          <button onClick={onAddCollection} type="button">
            <Plus size={15} /> 收藏一条来源
          </button>
          <button onClick={onAddNote} type="button">
            <FileText size={15} /> 新建个人笔记
          </button>
        </section>
        <section className="agent-principle">
          <Library size={17} />
          <p>回答只基于当前用户的收藏与笔记，并保留对应 <code>source_id</code>。</p>
        </section>
      </aside>
    </section>
  );
}
