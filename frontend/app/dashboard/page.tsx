export default function DashboardPage() {
  const POWER_BI_EMBED_URL = process.env.NEXT_PUBLIC_POWER_BI_URL ?? "";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">BI Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">
          Interactive Power BI reports — salary trends, skill heatmaps, district
          analysis
        </p>
      </div>

      {POWER_BI_EMBED_URL ? (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <iframe
            src={POWER_BI_EMBED_URL}
            width="100%"
            height="700"
            allowFullScreen
            className="border-0"
            title="Nepal Jobs Power BI Dashboard"
          />
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-xl p-12 text-center">
          <div className="max-w-sm mx-auto">
            <div className="w-12 h-12 bg-gray-100 rounded-xl mx-auto mb-4 flex items-center justify-center">
              <svg
                className="w-6 h-6 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <h3 className="text-sm font-medium text-gray-900 mb-2">
              Power BI dashboard coming soon
            </h3>
            <p className="text-xs text-gray-400 mb-4">
              Connect your Power BI report by adding the embed URL to your
              environment variables.
            </p>
            <code className="text-xs bg-gray-100 text-gray-600 px-3 py-2 rounded-lg block text-left">
              NEXT_PUBLIC_POWER_BI_URL=https://app.powerbi.com/...
            </code>
          </div>
        </div>
      )}
    </div>
  );
}
