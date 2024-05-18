from locust import HttpUser, TaskSet, task, between


class UserBehavior(TaskSet):
    @task
    def post_event(self):
        payload = "Avanan is a leading Enterprise Solution for Cloud Email and Collaboration Security, Checkpoint"
        self.client.post("/api/v1/events", data=payload)

    @task
    def get_stats(self):
        self.client.get("/api/v1/stats?interval=60")


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
