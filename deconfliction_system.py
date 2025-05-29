import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from datetime import datetime, timedelta

# Data structures
class Waypoint:
    def __init__(self, x, y, z, time):
        self.x = x
        self.y = y
        self.z = z
        self.time = time  # datetime object

class Mission:
    def __init__(self, waypoints, t_start, t_end):
        self.waypoints = waypoints
        self.t_start = t_start
        self.t_end = t_end

# Sample data: Primary mission and simulated schedules
def generate_sample_data():
    t_start = datetime(2025, 5, 28, 10, 0)
    t_end = datetime(2025, 5, 28, 10, 10)
    primary_waypoints = [
        Waypoint(0, 0, 100, t_start),
        Waypoint(50, 50, 100, t_start + timedelta(minutes=2)),
        Waypoint(100, 100, 100, t_start + timedelta(minutes=4)),
        Waypoint(150, 150, 100, t_start + timedelta(minutes=6))
    ]
    primary_mission = Mission(primary_waypoints, t_start, t_end)
    schedules = [
        Mission([
            Waypoint(200, 200, 100, t_start),
            Waypoint(250, 250, 100, t_start + timedelta(minutes=3)),
            Waypoint(300, 300, 100, t_start + timedelta(minutes=6))
        ], t_start, t_end),
        Mission([
            Waypoint(40, 40, 100, t_start + timedelta(minutes=1)),
            Waypoint(50, 50, 100, t_start + timedelta(minutes=2)),
            Waypoint(60, 60, 100, t_start + timedelta(minutes=3))
        ], t_start, t_end)
    ]
    return primary_mission, schedules

# Spatial check: Calculate Euclidean distance
def check_spatial_conflict(wp1, wp2, safety_buffer=10.0):
    distance = np.sqrt((wp1.x - wp2.x)**2 + (wp1.y - wp2.y)**2 + (wp1.z - wp2.z)**2)
    return distance < safety_buffer

# Temporal check: Check time overlap
def check_temporal_conflict(t1, t2, time_buffer=timedelta(seconds=30)):
    return abs((t1 - t2).total_seconds()) < time_buffer.total_seconds()

# Deconfliction check
def check_mission_conflicts(primary_mission, schedules):
    conflicts = []
    for i, schedule in enumerate(schedules):
        for wp1 in primary_mission.waypoints:
            for wp2 in schedule.waypoints:
                if check_spatial_conflict(wp1, wp2):
                    if check_temporal_conflict(wp1.time, wp2.time):
                        conflicts.append({
                            'drone_id': i,
                            'location': (wp2.x, wp2.y, wp2.z),
                            'time': wp2.time,
                            'primary_time': wp1.time
                        })
    status = "clear" if not conflicts else "conflict detected"
    return status, conflicts

# Visualization: 2D/3D plots and 4D animation
def visualize_mission(primary_mission, schedules, conflicts, animate_4d=False):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    px = [wp.x for wp in primary_mission.waypoints]
    py = [wp.y for wp in primary_mission.waypoints]
    pz = [wp.z for wp in primary_mission.waypoints]
    ax.plot(px, py, pz, 'b-', label='Primary Mission', marker='o')
    colors = ['r', 'g', 'm']
    for i, schedule in enumerate(schedules):
        sx = [wp.x for wp in schedule.waypoints]
        sy = [wp.y for wp in schedule.waypoints]
        sz = [wp.z for wp in schedule.waypoints]
        ax.plot(sx, sy, sz, f'{colors[i % len(colors)]}-', label=f'Drone {i}', marker='s')
    for conflict in conflicts:
        ax.scatter(conflict['location'][0], conflict['location'][1], conflict['location'][2],
                   c='y', s=100, marker='x', label='Conflict' if conflicts.index(conflict) == 0 else "")
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.legend()
    plt.title('Drone Trajectories and Conflicts')
    if animate_4d:
        def update(num):
            ax.clear()
            t = primary_mission.waypoints[0].time + timedelta(seconds=num * 30)
            ax.plot(px, py, pz, 'b-', label='Primary Mission', marker='o')
            for i, schedule in enumerate(schedules):
                sx = [wp.x for wp in schedule.waypoints if abs((wp.time - t).total_seconds()) < 30]
                sy = [wp.y for wp in schedule.waypoints if abs((wp.time - t).total_seconds()) < 30]
                sz = [wp.z for wp in schedule.waypoints if abs((wp.time - t).total_seconds()) < 30]
                if sx:
                    ax.scatter(sx, sy, sz, c=colors[i % len(colors)], marker='s', label=f'Drone {i}')
            ax.set_xlabel('X (m)')
            ax.set_ylabel('Y (m)')
            ax.set_zlabel('Z (m)')
            ax.set_title(f'Time: {t.strftime("%H:%M:%S")}')
            ax.legend()
        ani = animation.FuncAnimation(fig, update, frames=20, interval=500, blit=False)
        plt.show()
    else:
        plt.savefig('drone_trajectories.png')
        plt.show()

# Query interface
def deconfliction_query(primary_mission, schedules, visualize=True, animate_4d=False):
    status, conflicts = check_mission_conflicts(primary_mission, schedules)
    if visualize:
        visualize_mission(primary_mission, schedules, conflicts, animate_4d)
    return status, conflicts

# Test cases
def run_tests():
    primary_mission, schedules = generate_sample_data()
    status, conflicts = deconfliction_query(primary_mission, schedules, visualize=False)
    print("Test 1 - Full Mission Check:")
    print(f"Status: {status}")
    for c in conflicts:
        print(f"Conflict with Drone {c['drone_id']} at {c['location']} at {c['time']}")
    schedules[1].waypoints[1] = Waypoint(200, 200, 100, schedules[1].waypoints[1].time)
    status, conflicts = deconfliction_query(primary_mission, schedules, visualize=False)
    print("\nTest 2 - Conflict-Free Scenario:")
    print(f"Status: {status}")
    schedules[1].waypoints[1] = Waypoint(50, 50, 100, primary_mission.t_start + timedelta(minutes=10))
    status, conflicts = deconfliction_query(primary_mission, schedules, visualize=False)
    print("\nTest 3 - Same Location, Different Time:")
    print(f"Status: {status}")

if __name__ == "__main__":
    primary_mission, schedules = generate_sample_data()
    status, conflicts = deconfliction_query(primary_mission, schedules, visualize=True, animate_4d=True)
    print(f"Mission Status: {status}")
    for c in conflicts:
        print(f"Conflict with Drone {c['drone_id']} at {c['location']} at {c['time']}")
    run_tests()
