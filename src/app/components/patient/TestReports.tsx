import { useState } from 'react';
import { motion } from 'motion/react';
import { Upload, FileText, Download, Eye, AlertCircle, CheckCircle2, Brain } from 'lucide-react';

interface Report {
  id: number;
  name: string;
  type: string;
  date: string;
  status: 'analyzed' | 'processing' | 'pending';
  aiSummary?: string;
  abnormalMarkers?: string[];
}

const mockReports: Report[] = [
  {
    id: 1,
    name: 'Complete Blood Count (CBC)',
    type: 'Blood Test',
    date: '2026-02-20',
    status: 'analyzed',
    aiSummary: 'All values within normal range. No concerning markers detected.',
    abnormalMarkers: []
  },
  {
    id: 2,
    name: 'Tumor Marker Analysis',
    type: 'Cancer Screening',
    date: '2026-02-15',
    status: 'analyzed',
    aiSummary: 'CEA and CA 19-9 levels normal. No indication of malignancy.',
    abnormalMarkers: []
  },
  {
    id: 3,
    name: 'Chest X-Ray',
    type: 'Imaging',
    date: '2026-02-10',
    status: 'analyzed',
    aiSummary: 'Clear lung fields. No masses or abnormalities detected.',
    abnormalMarkers: []
  }
];

export default function TestReports() {
  const [reports] = useState<Report[]>(mockReports);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    // Handle file upload here
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold">Test Reports</h2>
        <p className="text-muted-foreground">Upload and manage your medical test reports</p>
      </div>

      {/* Upload Area */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`p-8 rounded-2xl border-2 border-dashed transition-all ${
          dragActive 
            ? 'border-primary bg-primary/5' 
            : 'border-border hover:border-primary hover:bg-muted/50'
        }`}
      >
        <div className="text-center">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#0B3C5D] to-[#1CA7A6] flex items-center justify-center mx-auto mb-4">
            <Upload className="w-8 h-8 text-white" />
          </div>
          <h3 className="font-semibold mb-2">Upload Medical Reports</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Drag and drop your PDF or image files here, or click to browse
          </p>
          <button className="px-6 py-2 bg-gradient-to-r from-[#0B3C5D] to-[#1CA7A6] text-white rounded-xl hover:shadow-lg transition-all">
            Choose Files
          </button>
          <p className="text-xs text-muted-foreground mt-4">
            Supported formats: PDF, JPG, PNG (Max 10MB)
          </p>
        </div>
      </div>

      {/* AI Analysis Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border border-border">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center flex-shrink-0">
            <Brain className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="font-semibold mb-2">AI-Powered Analysis</h3>
            <p className="text-sm text-muted-foreground">
              Our advanced AI automatically analyzes your reports, identifies abnormal markers, 
              and provides easy-to-understand summaries within minutes.
            </p>
          </div>
        </div>
      </div>

      {/* Reports List */}
      <div className="space-y-4">
        {reports.map((report, idx) => (
          <motion.div
            key={report.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="p-6 rounded-2xl bg-white dark:bg-slate-800 border border-border hover:shadow-lg transition-all"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center flex-shrink-0">
                  <FileText className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold mb-1">{report.name}</h3>
                  <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <span>{report.type}</span>
                    <span>•</span>
                    <span>{new Date(report.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {report.status === 'analyzed' && (
                  <span className="flex items-center gap-1 px-3 py-1 rounded-full bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 text-sm">
                    <CheckCircle2 className="w-4 h-4" />
                    Analyzed
                  </span>
                )}
              </div>
            </div>

            {report.aiSummary && (
              <div className="p-4 rounded-xl bg-muted mb-4">
                <p className="text-sm font-semibold mb-2">AI Summary:</p>
                <p className="text-sm text-muted-foreground">{report.aiSummary}</p>
              </div>
            )}

            {report.abnormalMarkers && report.abnormalMarkers.length > 0 ? (
              <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 mb-4">
                <div className="flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold text-amber-900 dark:text-amber-400 mb-1">
                      Abnormal Markers Detected
                    </p>
                    <ul className="text-sm text-amber-800 dark:text-amber-300 list-disc list-inside">
                      {report.abnormalMarkers.map((marker, i) => (
                        <li key={i}>{marker}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 mb-4">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <p className="text-sm text-green-900 dark:text-green-400">
                    All markers within normal range
                  </p>
                </div>
              </div>
            )}

            <div className="flex gap-3">
              <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-white hover:opacity-90 transition-opacity">
                <Eye className="w-4 h-4" />
                <span>View Report</span>
              </button>
              <button className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border hover:bg-muted transition-colors">
                <Download className="w-4 h-4" />
                <span>Download</span>
              </button>
              <button className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border hover:bg-muted transition-colors">
                <Brain className="w-4 h-4" />
                <span>AI Insights</span>
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
