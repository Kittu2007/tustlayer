"use client";

import { useState } from "react";
import { UploadPanel } from "@/components/product/UploadPanel";
import { PhonePreview } from "@/components/product/PhonePreview";
import { ResultsPanel } from "@/components/product/ResultsPanel";
import { useLenisScroll } from "@/hooks/useLenisScroll";

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

export default function ProductPage() {
  useLenisScroll();

  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [uploadedName, setUploadedName] = useState<string>("");
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [scanResults, setScanResults] = useState<ScanResponse>(null);

  const handleFileSelect = (file: File) => {
    setUploadedName(file.name);
    setScanResults(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target?.result && typeof e.target.result === "string") {
        setUploadedImage(e.target.result);
      }
    };
    reader.readAsDataURL(file);
  };

  const handleScan = async () => {
    if (!uploadedImage) return;

    setIsScanning(true);
    try {
      // Convert base64 data URL to a blob
      const responseBlob = await fetch(uploadedImage);
      const blob = await responseBlob.blob();
      
      const formData = new FormData();
      formData.append("file", blob, uploadedName || "screenshot.png");

      const response = await fetch("/api/v1/scan/execute", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setScanResults(data);
    } catch (error) {
      console.error("Forensic scan failed:", error);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="product-page">
      <div className="product-layout">
        <UploadPanel
          onFileSelect={handleFileSelect}
          uploadedImage={uploadedImage}
          uploadedName={uploadedName}
          onScan={handleScan}
          isScanning={isScanning}
          hasResults={!!scanResults}
        />
        
        <PhonePreview uploadedImage={uploadedImage} isScanning={isScanning} />
        
        <ResultsPanel results={scanResults} isScanning={isScanning} />
      </div>
    </div>
  );
}
