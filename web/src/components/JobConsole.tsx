import { AlertTriangle, CheckCircle2, Clock3, Play, ScrollText, Square, XCircle } from "lucide-react";
import { useEffect, useState } from "react";

import { api, streamJob } from "../api/client";
import type { Job } from "../api/client";

type Props = {
  activeJob: Job | null;
  onActiveJob: (job: Job | null) => void;
};

function StatusIcon({ status }: { status: string }) {
  if (status === "succeeded") return <CheckCircle2 size={14} />;
  if (status === "failed") return <XCircle size={14} />;
  if (status === "cancelled") return <AlertTriangle size={14} />;
  if (status === "running") return <Play size={14} />;
  return <Clock3 size={14} />;
}

export default function JobConsole({ activeJob, onActiveJob }: Props) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [log, setLog] = useState("");
  const [error, setError] = useState("");

  const refresh = () => api.jobs().then((data) => setJobs(data.jobs));

  const cancelActiveJob = async () => {
    if (!activeJob) return;
    await api.cancelJob(activeJob.id);
    await refresh();
  };

  useEffect(() => {
    refresh();
    const timer = window.setInterval(refresh, 2500);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!activeJob) return;
    setLog("");
    setError("");
    let cancelled = false;
    streamJob(activeJob.id, {
      onChunk(chunk) {
        if (!cancelled) setLog((prev) => prev + chunk);
      },
      onError(err) {
        if (!cancelled) setError(err.message);
      },
      onDone() {
        refresh();
      }
    });
    return () => {
      cancelled = true;
    };
  }, [activeJob?.id]);

  return (
    <section className="job-console">
      <div className="section-head">
        <div>
          <span className="eyebrow">Jobs</span>
          <h2>任务日志</h2>
        </div>
        <ScrollText size={18} />
      </div>
      <div className="job-list">
        {jobs.slice(0, 6).map((job) => (
          <button key={job.id} className={activeJob?.id === job.id ? "active" : ""} onClick={() => onActiveJob(job)}>
            <StatusIcon status={job.status} />
            <span>{job.kind}</span>
            <small>{job.status}</small>
          </button>
        ))}
        {activeJob?.status === "running" && (
          <button className="danger-action" onClick={() => void cancelActiveJob()}>
            <Square size={13} />
            <span>取消</span>
          </button>
        )}
      </div>
      <pre className="job-log">{log || (activeJob ? "等待日志..." : "选择或启动一个任务")}</pre>
      {error && <div className="error-note">{error}</div>}
    </section>
  );
}
