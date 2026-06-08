import '../App.css';
import type { PoolOption } from '../types';

interface SettingsProps {
  pools: PoolOption[] | null;
  selectedPoolId: string;
  setSelectedPoolId: (value: string) => void;
  seedInput: string;
  setSeedInput: (value: string) => void;
  roundsInput: string;
  setRoundsInput: (value: string) => void;
}

const Settings = ({
  pools,
  selectedPoolId,
  setSelectedPoolId,
  seedInput,
  setSeedInput,
  roundsInput,
  setRoundsInput,
}: SettingsProps) => {
  return (
    <div className="board-config">
      <label>
        Pool:{' '}
        <select
          value={selectedPoolId || pools?.[0]?.id || ''}
          onChange={(e) => setSelectedPoolId(e.target.value)}
          disabled={!pools || pools.length === 0}
        >
          {pools && pools.length > 0 ? (
            pools.map((p) => (
              <option key={p.id} value={p.id}>
                {p.display_name}
              </option>
            ))
          ) : (
            <option value="">No pools available</option>
          )}
        </select>
      </label>
      <label>
        Seed:{' '}
        <input
          type="number"
          min={0}
          max={2 ** 32 - 1}
          placeholder="Random"
          value={seedInput}
          onChange={(e) => setSeedInput(e.target.value)}
        />
      </label>
      <label>
        Rounds:{' '}
        <input
          type="number"
          min={1}
          max={50}
          value={roundsInput}
          onChange={(e) => setRoundsInput(e.target.value)}
        />
      </label>
    </div>
  );
};

export default Settings;
