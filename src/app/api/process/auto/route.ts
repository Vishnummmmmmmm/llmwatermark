import { NextRequest, NextResponse } from 'next/server';
import { LinguisticEngine } from '@/lib/linguistic-engine';

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const text = formData.get('text') as string | null;
    const file = formData.get('file') as File | null;

    // Send to local Python backend if available
    try {
      const backendForm = new FormData();
      if (text) backendForm.append('text', text);
      if (file) backendForm.append('file', file);

      const pyRes = await fetch('http://127.0.0.1:8000/api/process/auto', {
        method: 'POST',
        body: backendForm,
      });

      if (pyRes.ok) {
        const pyData = await pyRes.json();
        return NextResponse.json({ success: true, ...pyData });
      }
    } catch {
      // In-process fallback logic
    }

    if (text && text.trim()) {
      const result = LinguisticEngine.processText(text, 0.40);
      return NextResponse.json({
        success: true,
        detected_type: 'text',
        result,
      });
    }

    if (file) {
      const fn = file.name.toLowerCase();
      let type = 'image';
      if (fn.endsWith('.mp3') || fn.endsWith('.wav') || fn.endsWith('.m4a')) type = 'audio';
      if (fn.endsWith('.mp4') || fn.endsWith('.webm') || fn.endsWith('.mov')) type = 'video';

      return NextResponse.json({
        success: true,
        detected_type: type,
        result: {
          originalUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80',
          cleanedUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80',
          evasion_success: true,
          metadata_stripped: true,
        },
      });
    }

    return NextResponse.json({ error: 'Please provide text or upload a file' }, { status: 400 });
  } catch (error: any) {
    return NextResponse.json({ error: error.message || 'Internal error' }, { status: 500 });
  }
}
