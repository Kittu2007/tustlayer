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
    verdict?: string;
    extraction_quality_label?: string;
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
    image_quality_score?: number;
    ocr_pass_count?: number;
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

function getVerdictStyle(verdict: string): { color: string; icon: string } {
  const v = verdict.toLowerCase();
  if (v.includes("verified"))
    return { color: "#31f58b", icon: "✓" };
  if (v.includes("likely authentic"))
    return { color: "#31f58b", icon: "◉" };
  if (v.includes("partial verification"))
    return { color: "#ffb22e", icon: "◎" };
  if (v.includes("low confidence") || v.includes("verification recommended"))
    return { color: "#ffb22e", icon: "⚠" };
  if (v.includes("needs review"))
    return { color: "#ff9466", icon: "⚡" };
  if (v.includes("fake"))
    return { color: "#ffb59d", icon: "✕" };
  return { color: "#8899aa", icon: "?" };
}

function getQualityBadgeStyle(label: string): { bg: string; text: string } {
  const l = label.toLowerCase();
  if (l.includes("high quality"))
    return { bg: "rgba(49, 245, 139, 0.12)", text: "#31f58b" };
  if (l.includes("good"))
    return { bg: "rgba(49, 245, 139, 0.08)", text: "#7bf5a8" };
  if (l.includes("partial"))
    return { bg: "rgba(255, 178, 46, 0.10)", text: "#ffb22e" };
  if (l.includes("low"))
    return { bg: "rgba(255, 148, 102, 0.10)", text: "#ff9466" };
  return { bg: "rgba(255, 100, 80, 0.10)", text: "#ff6450" };
}

export function ResultsPanel({ results }: ResultsPanelProps) {
  if (!results) {
    return (
      <div className="product-panel results-panel" style={{ display: "grid", placeItems: "center", minHeight: "300px", padding: "20px", textAlign: "center", color: "var(--foreground-dim)" }}>
        <p>Upload a screenshot and execute a scan to see forensic results.</p>
      </div>
    );
  }

  const { trust_score_data, ocr_data, fraud_intelligence_data, metadata } = results;

  const finalVerdict = trust_score_data.verdict || "Analysis Complete";
  const verdictStyle = getVerdictStyle(finalVerdict);
  
  const ocrConfidencePct = Math.round(ocr_data.confidence_score * 100);
  const qualityLabel = trust_score_data.extraction_quality_label;
  const qualityBadge = qualityLabel ? getQualityBadgeStyle(qualityLabel) : null;

  const scoreColor = verdictStyle.color;
  const imageQualityPct = ocr_data.image_quality_score != null 
    ? Math.round(ocr_data.image_quality_score * 100) 
    : null;

  return (
    <div className="product-panel results-panel">
      <div className="product-panel-header">
        <span className="dot" /> Forensic Results
      </div>

      <div className="result-block">
        <div className="result-score">
          <div className="result-score-number" style={{ color: scoreColor }}>
            {Math.round(trust_score_data.trust_score)}
          </div>
          <div className="result-score-label">Trust Score</div>
          <div className="result-verdict">
            <span>Verdict</span>
            <strong style={{ color: verdictStyle.color }}>
              {verdictStyle.icon} {finalVerdict}
            </strong>
          </div>
          {qualityLabel && qualityBadge && (
            <div
              style={{
                marginTop: "8px",
                display: "inline-block",
                padding: "4px 12px",
                borderRadius: "20px",
                fontSize: "0.72rem",
                fontWeight: 500,
                letterSpacing: "0.04em",
                background: qualityBadge.bg,
                color: qualityBadge.text,
                border: `1px solid ${qualityBadge.text}22`,
              }}
            >
              {qualityLabel}
            </div>
          )}
        </div>
      </div>

      <div className="result-block">
        <h4 className="result-block-title" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          OCR Data
          <span
            style={{
              fontSize: "0.68rem",
              fontWeight: 400,
              padding: "2px 8px",
              borderRadius: "10px",
              background: ocrConfidencePct >= 70 ? "rgba(49,245,139,0.10)" : ocrConfidencePct >= 40 ? "rgba(255,178,46,0.10)" : "rgba(255,100,80,0.10)",
              color: ocrConfidencePct >= 70 ? "#31f58b" : ocrConfidencePct >= 40 ? "#ffb22e" : "#ff6450",
            }}
          >
            {ocrConfidencePct}% confidence
          </span>
        </h4>
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
        {imageQualityPct != null && (
          <div className="result-row">
            <span className="label">Image Quality</span>
            <span className="value">{imageQualityPct}%</span>
          </div>
        )}
        {ocr_data.ocr_pass_count != null && ocr_data.ocr_pass_count > 1 && (
          <div className="result-row">
            <span className="label">OCR Passes</span>
            <span className="value">{ocr_data.ocr_pass_count} passes (multi-pass consensus)</span>
          </div>
        )}
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
