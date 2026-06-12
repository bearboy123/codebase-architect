/**
 * Main application component
 */
import { useState } from 'react';
import { Header, Footer } from './components/Layout';
import { UploadPage } from './pages/UploadPage';
import { AnalysisDashboard } from './pages/AnalysisDashboard';
import './index.css';

function App() {
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);

  return (
    <div className="flex flex-col min-h-screen">
      <Header />

      <main className="flex-1">
        {!currentJobId ? (
          <UploadPage onAnalysisStart={setCurrentJobId} />
        ) : (
          <AnalysisDashboard jobId={currentJobId} onBack={() => setCurrentJobId(null)} />
        )}
      </main>

      <Footer />
    </div>
  );
}

export default App;
