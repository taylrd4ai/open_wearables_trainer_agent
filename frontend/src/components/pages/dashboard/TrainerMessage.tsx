import { Card } from '../../ui/Card';
import type { TrainerMessage as TrainerMessageType } from '../../../lib/api/types';

interface TrainerMessageProps {
  data: TrainerMessageType;
}

const personaStyles: Record<string, { border: string; bg: string; text: string; label: string; font: string }> = {
  hard_ass: {
    border: 'border-red-700',
    bg: 'bg-red-950/30',
    text: 'text-red-300',
    label: 'Hard Ass Coach',
    font: 'font-black uppercase tracking-wider',
  },
  encouraging: {
    border: 'border-green-700',
    bg: 'bg-green-950/30',
    text: 'text-green-300',
    label: 'Supportive Coach',
    font: 'font-medium italic',
  },
  balanced: {
    border: 'border-blue-700',
    bg: 'bg-blue-950/30',
    text: 'text-blue-300',
    label: 'Balanced Coach',
    font: 'font-normal',
  },
  standard: {
    border: 'border-gray-700',
    bg: 'bg-gray-800/50',
    text: 'text-gray-300',
    label: 'AI Trainer',
    font: 'font-normal',
  },
};

export function TrainerMessage({ data }: TrainerMessageProps) {
  if (!data) return null;
  const style = personaStyles[data.persona_mode] || personaStyles.standard;

  return (
    <Card className={`border-l-4 ${style.border} ${style.bg}`}>
      <div className="flex items-center justify-between mb-3">
        <span className={`text-xs ${style.text} ${style.font}`}>{style.label}</span>
        <span className="text-xs text-gray-500">
          {data.timestamp ? new Date(data.timestamp).toLocaleString() : ''}
        </span>
      </div>
      <p className={`text-sm leading-relaxed ${style.text} ${style.font}`}>
        {data.message}
      </p>
    </Card>
  );
}
