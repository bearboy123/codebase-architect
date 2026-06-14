/**
 * Header component
 */
export function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Codebase Architect</h1>
            <p className="text-gray-600 mt-1">AI-powered multi-agent code analysis</p>
          </div>
          <div className="text-right text-sm text-gray-500">
            <p>v0.1.0</p>
          </div>
        </div>
      </div>
    </header>
  );
}

/**
 * Footer component
 */
export function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-400 text-sm py-8 mt-12">
      <div className="max-w-7xl mx-auto px-6">
        <p>&copy; 2026 Codebase Architect Agent. Powered by Semantic Kernel and Azure OpenAI.</p>
      </div>
    </footer>
  );
}

/**
 * Loading spinner component
 */
export function LoadingSpinner({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative w-12 h-12 mb-4">
        <div className="absolute inset-0 border-4 border-gray-200 rounded-full"></div>
        <div className="absolute inset-0 border-4 border-transparent border-t-blue-600 rounded-full animate-spin"></div>
      </div>
      <p className="text-gray-600">{message}</p>
    </div>
  );
}

/**
 * Error message component
 */
export function ErrorMessage({ message, onDismiss }: { message: string; onDismiss?: () => void }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 flex items-start justify-between">
      <div>
        <h3 className="font-semibold text-red-800">Error</h3>
        <p className="text-red-700 mt-1">{message}</p>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="text-red-600 hover:text-red-700">
          ×
        </button>
      )}
    </div>
  );
}

/**
 * Success message component
 */
export function SuccessMessage({ message, onDismiss }: { message: string; onDismiss?: () => void }) {
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4 flex items-start justify-between">
      <div>
        <h3 className="font-semibold text-green-800">Success</h3>
        <p className="text-green-700 mt-1">{message}</p>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="text-green-600 hover:text-green-700">
          ×
        </button>
      )}
    </div>
  );
}

/**
 * Progress bar component
 */
export function ProgressBar({ progress }: { progress: number }) {
  return (
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div
        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
        style={{ width: `${progress}%` }}
      ></div>
    </div>
  );
}
