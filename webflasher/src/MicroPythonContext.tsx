import React, { createContext, useContext, useState, useCallback } from 'react';
// @ts-ignore
import { MicroPython } from './micropython-webserial.js';


type MicroPythonContextType = {
  mp: MicroPython | null;
  isConnected: boolean;
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  error: Error | null;
};

export const MicroPythonContext = createContext<MicroPythonContextType>({
  mp: null,
  isConnected: false,
  connect: async () => {},
  disconnect: async () => {},
  error: null,
});


type Props = { children: React.ReactNode };

export function MicroPythonProvider({ children }: Props) {
  const [mp, setMp] = useState<MicroPython | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const connect = useCallback(async () => {
    try {
      const mpInstance = new MicroPython();
      await mpInstance.connect();
      setMp(mpInstance);
      setIsConnected(true);
      setError(null);
    } catch (e: any) {
      setError(e instanceof Error ? e : new Error(String(e)));
      setIsConnected(false);
      setMp(null);
    }
  }, []);

  const disconnect = useCallback(async () => {
    if (mp) {
      await mp.disconnect();
      setIsConnected(false);
      setMp(null);
    }
  }, [mp]);

  return (
    <MicroPythonContext.Provider value={{ mp, isConnected, connect, disconnect, error }}>
      {children}
    </MicroPythonContext.Provider>
  );
}

export function useMicroPython() {
  return useContext(MicroPythonContext);
}
