/**
 * Frontend logging utility
 * Supports DEBUG, INFO, WARN, ERROR levels
 * Logs to console and localStorage for debugging
 */

type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  data?: unknown;
}

const LOG_LEVELS: Record<LogLevel, number> = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
};

const LOG_COLORS: Record<LogLevel, string> = {
  DEBUG: '#7C3AED', // purple
  INFO: '#3B82F6', // blue
  WARN: '#F59E0B', // amber
  ERROR: '#EF4444', // red
};

class Logger {
  private minLevel: LogLevel;
  private logs: LogEntry[] = [];
  private maxStoredLogs: number = 100;
  private readonly STORAGE_KEY = 'app_logs';

  constructor(minLevel?: LogLevel) {
    // Default to DEBUG in development, INFO in production
    const isDevelopment = import.meta.env.DEV;
    this.minLevel = minLevel || (isDevelopment ? 'DEBUG' : 'INFO');
    this.loadStoredLogs();
  }

  private formatTimestamp(): string {
    return new Date().toISOString();
  }

  private shouldLog(level: LogLevel): boolean {
    return LOG_LEVELS[level] >= LOG_LEVELS[this.minLevel];
  }

  private formatMessage(level: LogLevel, message: string): string {
    return `[${this.formatTimestamp()}] [${level}] ${message}`;
  }

  private logToConsole(level: LogLevel, message: string, data?: unknown): void {
    const color = LOG_COLORS[level];
    const style = `color: ${color}; font-weight: bold;`;
    const timestamp = this.formatTimestamp();

    if (data !== undefined) {
      console.log(
        `%c[${timestamp}] [${level}]`,
        style,
        message,
        data
      );
    } else {
      console.log(
        `%c[${timestamp}] [${level}]`,
        style,
        message
      );
    }
  }

  private storeLog(level: LogLevel, message: string, data?: unknown): void {
    const entry: LogEntry = {
      timestamp: this.formatTimestamp(),
      level,
      message,
      ...(data !== undefined && { data }),
    };

    this.logs.push(entry);

    // Keep only the last N logs in memory
    if (this.logs.length > this.maxStoredLogs) {
      this.logs = this.logs.slice(-this.maxStoredLogs);
    }

    // Also store to localStorage for persistence
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.logs));
    } catch (e) {
      // localStorage might be full or unavailable
      console.warn('Failed to store logs in localStorage', e);
    }
  }

  private loadStoredLogs(): void {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        this.logs = JSON.parse(stored);
      }
    } catch (e) {
      console.warn('Failed to load logs from localStorage', e);
    }
  }

  debug(message: string, data?: unknown): void {
    if (!this.shouldLog('DEBUG')) return;
    this.logToConsole('DEBUG', message, data);
    this.storeLog('DEBUG', message, data);
  }

  info(message: string, data?: unknown): void {
    if (!this.shouldLog('INFO')) return;
    this.logToConsole('INFO', message, data);
    this.storeLog('INFO', message, data);
  }

  warn(message: string, data?: unknown): void {
    if (!this.shouldLog('WARN')) return;
    this.logToConsole('WARN', message, data);
    this.storeLog('WARN', message, data);
  }

  error(message: string, data?: unknown): void {
    if (!this.shouldLog('ERROR')) return;
    this.logToConsole('ERROR', message, data);
    this.storeLog('ERROR', message, data);
  }

  /**
   * Get all stored logs
   */
  getAllLogs(): LogEntry[] {
    return [...this.logs];
  }

  /**
   * Get logs filtered by level
   */
  getLogsByLevel(level: LogLevel): LogEntry[] {
    return this.logs.filter(log => log.level === level);
  }

  /**
   * Clear all stored logs
   */
  clearLogs(): void {
    this.logs = [];
    try {
      localStorage.removeItem(this.STORAGE_KEY);
    } catch (e) {
      console.warn('Failed to clear logs from localStorage', e);
    }
  }

  /**
   * Export logs as JSON
   */
  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }

  /**
   * Set minimum log level
   */
  setLevel(level: LogLevel): void {
    this.minLevel = level;
  }
}

// Create global logger instance
// Automatically uses DEBUG in development, INFO in production
export const logger = new Logger();

// Export for testing/debugging in browser console
declare global {
  interface Window {
    __logger: typeof logger;
  }
}

if (typeof window !== 'undefined') {
  window.__logger = logger;
}
