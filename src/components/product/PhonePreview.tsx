"use client";

type PhonePreviewProps = {
  uploadedImage: string | null;
};

export function PhonePreview({ uploadedImage }: PhonePreviewProps) {
  return (
    <div className="preview-panel">
      <div className="product-panel-header" style={{ width: "100%", justifyContent: "center", borderBottom: "none", opacity: 0.6 }}>
        <span className="dot" /> Live Preview
      </div>
      
      <div className="preview-phone-wrap">
        <div className="preview-phone-glow" />
        <div className="phone-shell" style={{ visibility: "visible", opacity: 1 }}>
          <div className="phone-screen">
            <div className="phone-notch" />
            <div className="phone-topbar">
              <span>TrustLayer AI</span>
              <span className="live-dot">● LIVE</span>
            </div>
            
            {uploadedImage ? (
              <img 
                src={uploadedImage} 
                alt="Preview" 
                style={{ width: "100%", height: "85%", objectFit: "contain", marginTop: "10px", borderRadius: "8px" }} 
              />
            ) : (
              <div className="phone-receipt">
                <span className="phone-receipt-label">Sample Proof</span>
                <strong className="phone-receipt-title">Ramesh Kirana Store</strong>
                <div className="phone-receipt-amount">&#8377;4,500</div>
                <div className="phone-receipt-meta">
                  <span>9876543210@ybl</span>
                  <span>26 May</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
