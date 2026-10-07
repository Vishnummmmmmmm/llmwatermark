import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const video = formData.get('video') as File | null;
    const preserveAudio = formData.get('preserveAudio') === 'true';

    if (!video) {
      return NextResponse.json({ error: 'Video file is required' }, { status: 400 });
    }

    return NextResponse.json({
      success: true,
      originalUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
      cleanedUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
      frameCount: 240,
      audioStatus: preserveAudio ? 'Intact (Web Audio Remuxed)' : 'Muted',
      creditsUsed: 40,
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message || 'Internal error' }, { status: 500 });
  }
}
