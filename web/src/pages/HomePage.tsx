import { ClipboardList, FilePlus2, GitBranch, Newspaper, Play, ScrollText } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import { api } from "../api/client";
import type { HomeResponse, Job } from "../api/client";
import JobConsole from "../components/JobConsole";

type Props = {
  domain: string;
  onNavigate: (path: string) => void;
};

function parseArxivIds(text: string) {
  return Array.from(new Set(text.match(/\d{4}\.\d{4,5}/g) ?? []));
}

type PendingJob =
  | { kind: "read"; source: string; domain: string; command: string[]; impact: string }
  | { kind: "survey"; sources: string[]; domain: string; name?: string; command: string[]; impact: string }
  | { kind: "report"; topic: string; domain: string; command: string[]; impact: string };

function formatCommand(command: string[]) {
  return command.map((part) => (/\s/.test(part) ? JSON.stringify(part) : part)).join(" ");
}

function planCommand(text: string, domain: string): PendingJob {
  const ids = parseArxivIds(text);
  if (/survey|调研/i.test(text) && ids.length > 0) {
    const command = ["conda", "run", "-n", "paper_reader", "python", "paper_reader.py", "survey", ...ids, "--domain", domain];
    return {
      kind: "survey",
      sources: ids,
      domain,
      command,
      impact: `将生成或更新 ${domain}/surveys/ 下的调研列表；不会自动 git push。`
    };
  }
  if (/report|报告/i.test(text)) {
    const topic = text.replace(/^(生成|写|create)\s*/i, "").trim();
    const command = ["conda", "run", "-n", "paper_reader", "python", "paper_reader.py", "report", topic, "--domain", domain];
    return {
      kind: "report",
      topic,
      domain,
      command,
      impact: `将生成或更新 ${domain}/reports/ 下的报告；不会自动 git push。`
    };
  }
  if (ids.length > 0 || /read|添加|读/i.test(text)) {
    const source = ids[0] ?? text;
    const command = [
      "conda",
      "run",
      "-n",
      "paper_reader",
      "python",
      "paper_reader.py",
      "read",
      source,
      "--domain",
      domain,
      "--no-sync"
    ];
    return {
      kind: "read",
      source,
      domain,
      command,
      impact: `将读取论文并更新 ${domain}/papers/ 及必要的索引/方法文档；使用 --no-sync，不会自动 git push。`
    };
  }
  throw new Error("未识别到 read/survey/report 意图");
}

export default function HomePage({ domain, onNavigate }: Props) {
  const [home, setHome] = useState<HomeResponse | null>(null);
  const [command, setCommand] = useState("");
  const [activeJob, setActiveJob] = useState<Job | null>(null);
  const [pendingJob, setPendingJob] = useState<PendingJob | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.home(domain).then(setHome).catch((err: Error) => setError(err.message));
  }, [domain]);

  const runCommand = async (event: FormEvent) => {
    event.preventDefault();
    const text = command.trim();
    if (!text) return;
    setError("");
    try {
      setPendingJob(planCommand(text, domain));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  const confirmPendingJob = async () => {
    if (!pendingJob) return;
    setError("");
    try {
      let job: Job;
      if (pendingJob.kind === "read") {
        job = await api.startRead(pendingJob.source, pendingJob.domain, undefined, true);
      } else if (pendingJob.kind === "survey") {
        job = await api.startSurvey(pendingJob.sources, pendingJob.domain, pendingJob.name, undefined, true);
      } else {
        job = await api.startReport(pendingJob.topic, pendingJob.domain, [], undefined, true);
      }
      setActiveJob(job);
      setPendingJob(null);
      setCommand("");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  };

  const startMock = async (fail = false) => {
    const job = await api.startMock(domain, fail);
    setActiveJob(job);
  };

  return (
    <div className="home-page">
      <section className="console-band">
        <div>
          <span className="eyebrow">Workbench</span>
          <h1>论文阅读控制台</h1>
        </div>
        <div className="status-grid">
          <div><GitBranch size={15} /><span>{home?.git_status ? "dirty" : "clean"}</span></div>
          <div><Newspaper size={15} /><span>{home?.model ?? "model"}</span></div>
          <div><ClipboardList size={15} /><span>{home?.provider_ready ? "Codex ready" : "local fallback"}</span></div>
        </div>
      </section>

      <section className="command-panel">
        <form onSubmit={runCommand}>
          <FilePlus2 size={18} />
          <input
            value={command}
            onChange={(event) => setCommand(event.target.value)}
            placeholder="读 arXiv: 2504.16054 / survey 2504.16054 2410.24164 / 生成 report ..."
          />
          <button className="primary-button" disabled={!command.trim()}>
            <Play size={15} />
            <span>运行</span>
          </button>
        </form>
        <div className="command-actions">
          <button onClick={() => void startMock(false)}>日志自检</button>
          <button onClick={() => void startMock(true)}>失败自检</button>
        </div>
        {pendingJob && (
          <div className="confirm-panel">
            <div>
              <strong>确认启动 {pendingJob.kind}</strong>
              <p>{pendingJob.impact}</p>
              <code>{formatCommand(pendingJob.command)}</code>
            </div>
            <div className="confirm-actions">
              <button onClick={() => setPendingJob(null)}>取消</button>
              <button className="primary-button" onClick={() => void confirmPendingJob()}>
                <Play size={15} />
                <span>确认运行</span>
              </button>
            </div>
          </div>
        )}
        {error && <div className="error-note">{error}</div>}
      </section>

      <div className="home-grid">
        <section className="list-panel">
          <div className="section-head">
            <div>
              <span className="eyebrow">Recent</span>
              <h2>论文卡片</h2>
            </div>
            <Newspaper size={18} />
          </div>
          {home?.recent_papers.map((item) => (
            <button key={item.path} onClick={() => onNavigate(item.path)} className="row-card">
              <strong>{item.title}</strong>
              <span>{item.path}</span>
              <small>{item.snippet}</small>
            </button>
          ))}
        </section>

        <section className="list-panel">
          <div className="section-head">
            <div>
              <span className="eyebrow">Reports</span>
              <h2>交叉分析</h2>
            </div>
            <ScrollText size={18} />
          </div>
          {home?.recent_reports.map((item) => (
            <button key={item.path} onClick={() => onNavigate(item.path)} className="row-card">
              <strong>{item.title}</strong>
              <span>{item.path}</span>
              <small>{item.snippet}</small>
            </button>
          ))}
        </section>
      </div>

      <JobConsole activeJob={activeJob} onActiveJob={setActiveJob} />
    </div>
  );
}
