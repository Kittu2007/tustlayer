"use client";

type ScanResponse = {
  success: boolean;
  metadata: { execution_time_ms: number; modules_executed: string[] };
  trust_score_data: {
    trust_score: number;
    risk_level: string;
    fraud_probability: number;
    confidence_reasoning: string[];
    recommended_actions: string[];
  };
  ocr_data: {
    fields: {
      payment_amount: string | null;
      upi_transaction_id: string | null;
      receiver_name: string | null;
      timestamp: string | null;
      payment_app_name: string | null;
    };
    confidence_score: number;
    used_fallback: boolean;
  };
  fraud_intelligence_data: {
    fingerprint_match: boolean;
    match_confidence: number;
    match_count: number;
    fraud_type: string | null;
  };
} | null;

type ResultsPanelProps = {
  results: ScanResponse;
};

export function ResultsPanel({ results }: ResultsPanelProps) {
  if (!results) {
    return (
      <div className="product-panel results-panel" style={{ display: "grid", placeItems: "center", minHeight: "300px", padding: "20px", textAlign: "center", color: "var(--foreground-dim)" }}>
        <p>Upload a screenshot and execute a scan to see forensic results.</p>
      </div>
    );
  }

  const { trust_score_data, ocr_data, fraud_intelligence_data, metadata } = results;

  const isHighRisk = trust_score_data.risk_level === "HIGH";
  const isMedRisk = trust_score_data.risk_level === "MEDIUM";

  const verdictLabel = isHighRisk ? "Likely Fake Proof" : isMedRisk ? "Suspicious" : "Authentic Payment";
  const verdictClass = isHighRisk ? "danger" : isMedRisk ? "warn" : "success";

  return (
    <div className="product-panel results-panel">
      <div className="product-panel-header">
        <span className="dot" /> Forensic Results
      </div>

      <div className="result-block">
        <div className="result-score">
          <div className="result-score-number" style={{ color: isHighRisk ? "var(--ember)" : isMedRisk ? "#ffb22e" : "#31f58b" }}>
            {Math.round(trust_score_data.trust_score)}
          </div>
          <div className="result-score-label">Trust Score</div>
          <div className="result-verdict">
            <span>Verdict</span>
            <strong style={{ color: isHighRisk ? "#ffb59d" : isMedRisk ? "#ffb22e" : "#31f58b" }}>{verdictLabel}</strong>
          </div>
        </div>
      </div>

      <div className="result-block">
        <h4 className="result-block-title">OCR Data</h4>
        <div className="result-row">
          <span className="label">Amount</span>
          <span className="value">&#8377;{ocr_data.fields.payment_amount || "N/A"}</span>
        </div>
        <div className="result-row">
          <span className="label">Transaction ID</span>
          <span className="value">{ocr_data.fields.upi_transaction_id || "N/A"}</span>
        </div>
        <div className="result-row">
          <span className="label">Receiver</span>
          <span className="value">{ocr_data.fields.receiver_name || "N/A"}</span>
        </div>
        <div className="result-row">
          <span className="label">Timestamp</span>
          <span className="value">{ocr_data.fields.timestamp || "N/A"}</span>
        </div>
        <div className="result-row">
          <span className="label">Payment App</span>
          <span className="value">{ocr_data.fields.payment_app_name || "N/A"}</span>
        </div>
      </div>

      <div className="result-block">
        <h4 className="result-block-title">Fraud Intelligence</h4>
        <div className="result-row">
          <span className="label">Template Match</span>
          <span className={`value ${fraud_intelligence_data.fingerprint_match ? "danger" : "success"}`}>
            {fraud_intelligence_data.fingerprint_match ? "DETECTED" : "CLEAR"}
          </span>
        </div>
        <div className="result-row">
          <span className="label">Confidence</span>
          <span className="value">{Math.round(fraud_intelligence_data.match_confidence * 100)}%</span>
        </div>
        <div className="result-row">
          <span className="label">Fraud Type</span>
          <span className="value">{fraud_intelligence_data.fraud_type || "N/A"}</span>
        </div>
      </div>

      <div className="result-block">
        <h4 className="result-block-title">AI Reasoning</h4>
        {trust_score_data.confidence_reasoning.map((reason, idx) => (
          <p key={idx} className="result-reason">{reason}</p>
        ))}
      </div>

      <div className="result-block">
        <h4 className="result-block-title">Recommended Actions</h4>
        {trust_score_data.recommended_actions.map((action, idx) => (
          <p key={idx} className="result-action">{action}</p>
        ))}
      </div>
      
      <div className="result-block">
        <h4 className="result-block-title">Scan Metadata</h4>
        <div className="result-row">
          <span className="label">Execution Time</span>
          <span className="value">{metadata.execution_time_ms}ms</span>
        </div>
      </div>
    </div>
  );
}
