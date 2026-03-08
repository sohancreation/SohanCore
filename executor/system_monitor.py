import psutil
import logging
import platform
import os
import signal

logger = logging.getLogger(__name__)

def get_system_stats():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
                                                       
        battery = psutil.sensors_battery()
        battery_pct = f"{battery.percent}%" if battery else "N/A"
        charging = battery.power_plugged if battery else False
        
        import socket
        import datetime
        import httpx
        
                  
        local_ip = socket.gethostbyname(socket.gethostname())
        
                                
        public_ip = "Unknown"
        try:
            with httpx.Client() as client:
                public_ip = client.get("https://api.ipify.org", timeout=2).text
        except: pass
        
                
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.datetime.fromtimestamp(boot_time_timestamp)
        now = datetime.datetime.now()
        uptime = now - bt
        uptime_str = str(uptime).split('.')[0]                      
        
        stats = {
            "cpu_usage": f"{cpu_usage}%",
            "ram_usage": f"{ram.percent}%",
            "ram_total": f"{round(ram.total / (1024**3), 2)} GB",
            "disk_usage": f"{disk.percent}%",
            "disk_free": f"{round(disk.free / (1024**3), 2)} GB",
            "battery": battery_pct,
            "charging": charging,
            "os": f"{platform.system()} {platform.release()}",
            "local_ip": local_ip,
            "public_ip": public_ip,
            "uptime": uptime_str
        }
        
        msg = (
            f"📊 *System Health Report*\n\n"
            f"💻 *CPU:* {cpu_usage}%\n"
            f"🧠 *RAM:* {ram.percent}% ({stats['ram_total']} total)\n"
            f"💽 *Disk:* {disk.percent}% ({stats['disk_free']} free)\n"
            f"🔋 *Battery:* {battery_pct} {'(Charging)' if charging else ''}\n"
            f"🌐 *Network:* `{local_ip}` (Local), `{public_ip}` (Public)\n"
            f"⏱️ *Uptime:* {uptime_str}\n"
            f"🖥️ *OS:* {stats['os']}"
        )
        
        return {"status": "success", "message": msg, "stats": stats}
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        return {"status": "error", "message": str(e)}

def list_top_processes(count=5):
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
                                         
        top_procs = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:count]
        
        msg = "🔍 *Top 5 Active Processes:*\n\n"
        for p in top_procs:
            msg += f"• `{p['name']}` (CPU: {p['cpu_percent']}%, RAM: {round(p['memory_percent'], 1)}%)\n"
            
        return {"status": "success", "message": msg, "processes": top_procs}
    except Exception as e:
        logger.error(f"Failed to list processes: {e}")
        return {"status": "error", "message": str(e)}

def kill_process(name_or_pid):
    try:
        killed_count = 0
        if str(name_or_pid).isdigit():
                         
            pid = int(name_or_pid)
            p = psutil.Process(pid)
            p.terminate()
            return {"status": "success", "message": f"Terminated process with PID {pid}"}
        else:
                          
            name = str(name_or_pid).lower()
            for proc in psutil.process_iter(['name']):
                if name in proc.info['name'].lower():
                    proc.terminate()
                    killed_count += 1
            
            if killed_count > 0:
                return {"status": "success", "message": f"Terminated {killed_count} instances of '{name_or_pid}'"}
            else:
                return {"status": "error", "message": f"No process found matching '{name_or_pid}'"}
    except Exception as e:
        logger.error(f"Failed to kill process {name_or_pid}: {e}")
        return {"status": "error", "message": str(e)}
