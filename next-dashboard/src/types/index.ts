export interface Reading {
  id: number;
  created_at: string;
  temperature: number;
  setpoint: number;
  ssr_on: boolean;
  pid_output: number;
}

export interface Settings {
  id: number;
  setpoint: number;
  kp: number;
  ki: number;
  kd: number;
  cj_offset: number;
  running: boolean;
  updated_at: string;
}
