import { useEffect, useRef, useState } from 'react';

export const useBackgroundMusic = (
  audioPath: string,
  loop: boolean = true,
  volume: number = 0.3
) => {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    const audio = new Audio(audioPath);
    audio.loop = loop;
    audio.volume = volume;
    audioRef.current = audio;

    audio
      .play()
      .then(() => setIsPlaying(true))
      .catch((err) => console.log('Autoplay blocked:', err));

    return () => {
      audio.pause();
      audio.currentTime = 0;
    };
  }, [audioPath, volume, loop]);

  const toggleMute = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  return { isPlaying, toggleMute };
};
