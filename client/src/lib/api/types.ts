export interface DeviceTelemetry {
    device_id: string;
    device_type: "motor" | "hvac" | "compressor" | "lighting";
    status: "off" | "starting" | "running" | "fault";
    voltage: number;
    current: number;
    power: number;
    timestamp: number;
}

export interface GridContext {
    carbon_intensity: number;
    electricity_price: number;
    renewable_percentage: number;
    timestamp: number;
}

export interface DeviceListItem {
    device_id: string;
    device_type: string;
    status: string;
}

export interface DeviceListResponse {
    device_count: number;
    devices: DeviceListItem[];
}

export interface ControlResponse {
    status: string;
    message: string;
    device_status?: string;
}
