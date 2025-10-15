import React, { useEffect, useState } from "react";
import VideoPlayer from "../components/VideoPlayer";
import OverlayEditor from "../components/OverlayEditor";
import { getOverlays, startStream } from "../api/api";

const LandingPage = () => {
  const [overlays, setOverlays] = useState([]);
  const [hlsUrl, setHlsUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const fetchOverlays = async () => {
    try {
      const res = await getOverlays();
      setOverlays(res.data);
    } catch (error) {
      console.error("Error fetching overlays:", error);
    }
  };

  const handleStartStream = async () => {
    const rtspUrl = prompt("Enter RTSP URL:");
    if (!rtspUrl) return;

    setIsLoading(true);
    try {
      const res = await startStream(rtspUrl);
      setHlsUrl(`http://127.0.0.1:5000${res.data.hls_url}`);
    } catch (error) {
      console.error("Error starting stream:", error);
      alert("Failed to start stream. Please check the RTSP URL and try again.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchOverlays();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      {/* Header Section */}
      <div className="text-center mb-8">
        <h1 className="text-3xl md:text-5xl lg:text-6xl font-bold text-gray-800 mb-4">
          RTSP <span className="text-blue-600">Livestream</span> App
        </h1>
        <p className="text-gray-600 text-lg md:text-xl max-w-2xl mx-auto">
          Stream and manage your RTSP feeds with real-time overlay controls
        </p>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
        
        {/* Video Player Section */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Control Card */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
              <div>
                <h2 className="text-xl font-semibold text-gray-800">Stream Controls</h2>
                <p className="text-gray-600 text-sm">Start and manage your livestream</p>
              </div>
              <button 
                className={`${
                  isLoading 
                    ? 'bg-blue-400 cursor-not-allowed' 
                    : 'bg-blue-600 hover:bg-blue-700 transform hover:scale-105'
                } text-white font-semibold py-3 px-6 rounded-xl transition-all duration-200 active:scale-95 shadow-md hover:shadow-lg flex items-center gap-2 min-w-[160px] justify-center`}
                onClick={handleStartStream}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Starting...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Start Livestream
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Video Player Card */}
          {hlsUrl && (
            <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
              <div className="flex items-center gap-2 mb-4">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <h2 className="text-xl font-semibold text-gray-800">Live Stream</h2>
                <div className="flex items-center gap-2 ml-auto">
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-red-600 font-medium">LIVE</span>
                </div>
              </div>
              <div className="relative bg-black rounded-xl overflow-hidden aspect-video">
                <VideoPlayer hlsUrl={hlsUrl} />
                
                {/* Overlay rendering */}
                {overlays.map((ov) => (
                  <div
                    key={ov.name}
                    style={{
                      position: "absolute",
                      top: `${ov.y}%`,
                      left: `${ov.x}%`,
                      width: `${ov.width}%`,
                      height: `${ov.height}%`,
                      pointerEvents: "none",
                      zIndex: 10,
                    }}
                    className="transition-all duration-200"
                  >
                    {ov.type === "text" ? (
                      <div 
                        className="text-white font-semibold p-2 break-words h-full overflow-hidden"
                        style={{
                          textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
                          fontSize: `${Math.max(12, ov.height / 2)}px`
                        }}
                      >
                        {ov.content}
                      </div>
                    ) : (
                      <img 
                        src={ov.content} 
                        alt={ov.name} 
                        className="w-full h-full object-contain transition-all duration-200"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Overlay Editor Sidebar */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200 h-fit sticky top-6">
            <div className="flex items-center gap-2 mb-6">
              <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
              <h2 className="text-xl font-semibold text-gray-800">Overlay Manager</h2>
            </div>
            
            <OverlayEditor overlays={overlays} refreshOverlays={fetchOverlays} />
          </div>

          {/* Status Card */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
            <h3 className="font-semibold text-gray-800 mb-4">Stream Status</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Stream Active</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${hlsUrl ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                  {hlsUrl ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Active Overlays</span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                  {overlays.length}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Connection</span>
                <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                  {hlsUrl ? 'HLS' : 'Idle'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Empty State - Only show when no stream is active */}
      {!hlsUrl && !isLoading && (
        <div className="max-w-2xl mx-auto mt-16 text-center">
          <div className="bg-white rounded-2xl shadow-lg p-12 border-2 border-dashed border-gray-300">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">Ready to Stream</h3>
            <p className="text-gray-600 mb-6">Click the button above to start your livestream</p>
            <button 
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-xl transition-all duration-200 transform hover:scale-105"
              onClick={handleStartStream}
            >
              Start Streaming
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LandingPage;