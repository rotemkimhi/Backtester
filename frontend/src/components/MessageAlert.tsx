import type { MessageAlertProps } from "../interfaces";

export default function MessageAlert({ message, error }: MessageAlertProps) {
  if (!message) return null;
  return (
    <div className={error ? "error-message" : "success-message"}>
      {message}
    </div>
  );
}
