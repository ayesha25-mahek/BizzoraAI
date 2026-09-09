import React from 'react';

const Footer: React.FC = () => (
  <footer className="border-t border-white/8 py-4 mt-8">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-2">
      <span className="text-xs text-gray-600">
        © 2024 BizzoraAI · AI-Powered Content Transformation Engine
      </span>
      <span className="text-xs text-gray-700">
        Powered by · Gemini · Groq · ElevenLabs · Runway · Luma · HuggingFace · Cloudflare AI
      </span>
    </div>
  </footer>
);

export { Footer };
