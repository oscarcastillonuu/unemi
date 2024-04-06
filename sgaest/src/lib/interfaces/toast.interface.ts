export interface Toast {
  id?: number,
  type?: string,
  icon?: string,
  autohide?: boolean;
  body?: boolean;
  delay?: number;
  duration?: number;
  fade?: boolean;
  header?: string;
  isOpen?: boolean;
  bg?: string;
  toggle?: () => void;
}
