import math
from locust import HttpUser, TaskSet, task, constant
from locust import LoadTestShape


class UserTasks(TaskSet):
    @task
    def get_root(self):
        self.client.get("")
        self.client.get("1/results/")
        self.client.post("1/vote/", {"choice":1})


class WebsiteUser(HttpUser):
    wait_time = constant(0.5)
    tasks = [UserTasks]


class DoubleWave(LoadTestShape):
    """
    Shape to mimic the day of a normal user. This will send 2 peaks, first one
    at time_limit/3 and second one at 2*time_limit/3. Also, the program will
    terminate once time_limit time has elapsed. Also, you can set the minimum
    users at each time.
    For now, this program is generating load periodically with time period time_limit
    """
    min_users = 10
    peak_one_users = 100
    peak_two_users = 80
    time_limit = 600


    def tick(self):
        run_time = round(self.get_run_time())
        run_time %= self.time_limit
        if run_time < self.time_limit:
            user_count = (
                (self.peak_one_users - self.min_users)
                * math.e ** -(((run_time / (self.time_limit / 10 * 2 / 3)) - 5) ** 2)
                + (self.peak_two_users - self.min_users)
                * math.e ** -(((run_time / (self.time_limit / 10 * 2 / 3)) - 10) ** 2)
                + self.min_users
            )
            return (round(user_count), round(user_count))
        else:
            return None
