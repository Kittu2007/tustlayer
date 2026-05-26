"use client";

import { ChangeEvent, DragEvent, useRef } from "react";

type UploadPanelProps = {
  onFileSelect: (file: File) => void;
  uploadedImage: string | null;
  uploadedName: string;
  onScan: () => void;
  isScanning: boolean;
  hasResults: boolean;
};

export function UploadPanel({
  onFileSelect,
  uploadedImage,
  uploadedName,
  onScan,
  isScanning,
  hasResults,
}: UploadPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) {
      onFileSelect(file);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith("image/")) {
      onFileSelect(file);
    }
    // Reset input so the same file can be selected again
    e.target.value = "";
  };

  return (
    <div className="product-panel">
      <div className="product-panel-header">
        <span className="dot" /> Upload Zone
      </div>
      <div className="product-panel-body">
        <div
          className="upload-dropzone"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="upload-dropzone-icon">↑</div>
          <p>
            <strong>Click to upload</strong> or drag and drop
          </p>
          <div className="format-hint">PNG, JPG, JPEG</div>
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            style={{ display: "none" }}
            accept="image/*"
            onChange={handleFileChange}
          />
        </div>

        {uploadedImage && (
          <div className="upload-preview">
            <img src={uploadedImage} alt="Uploaded receipt" />
          </div>
        )}

        <button
          className="scan-btn"
          onClick={onScan}
          disabled={!uploadedImage || isScanning}
        >
          {isScanning ? "Scanning..." : "Execute Forensic Scan"}
        </button>
      </div>
    </div>
  );
}
