# Session 5 Lab — Kubernetes Fundamentals with kind and Jenkins CI/CD

This beginner lab uses a single AWS sandbox VM. A local Kubernetes cluster runs
inside the VM with **kind** (Kubernetes in Docker). Jenkins also runs in a Docker
container on the same VM.

## Lab outcome

By the end of the demonstration, trainees will be able to:

- identify a Kubernetes cluster, node, namespace, Deployment, Pod, and Service;
- use `kubectl` inside the sandbox VM to inspect an application;
- observe Kubernetes replace a deleted Pod;
- explain how a GitHub change becomes a tested Docker image and a Kubernetes rollout;
- verify the deployed application with an HTTP health check.

## Environment prepared for the class

| Item | Value |
| --- | --- |
| AWS VM public IP | `54.251.51.242` |
| AWS VM private IP | `172.31.33.10` |
| Jenkins | `http://54.251.51.242:8080` |
| Application | `http://54.251.51.242:8081` |
| Health endpoint | `http://54.251.51.242:8081/health` |
| Jenkins job | `session5-kind-cicd` |
| kind cluster | `session5` |
| kubectl context | `kind-session5` |
| Kubernetes namespace | `session5` |
| Deployment and Service | `training-app` |
| Desired replicas | `2` |

Jenkins username is `admin`. The instructor can retrieve the generated password
without storing it in this repository:

```bash
sudo cat /home/ubuntu/session5-kind-lab/.secrets/jenkins-admin-password
```

> Access to ports 8080 and 8081 is restricted by the AWS security group to the
> instructor's current public IP. If the network changes, the rule must be
> updated before the browser can connect.

## How the automated delivery works

1. Jenkins checks the public GitHub repository's `main` branch every minute.
2. A new commit starts the `session5-kind-cicd` pipeline.
3. Jenkins checks the Python syntax and runs three unit tests.
4. Jenkins builds an immutable local image tag such as
   `session5-training-app:4-a1b2c3d4e5f6`.
5. Jenkins loads that image into the `session5` kind cluster.
6. `kubectl apply` creates or updates the Deployment and NodePort Service.
7. Jenkins waits for the Deployment rollout and performs `/health` and `/`
   smoke tests.
8. Test results, the rendered manifest, resource details, and deployment metadata
   are retained as Jenkins build artifacts.

This is a classroom simulation. It intentionally loads the image directly into
kind, so registry credentials are not needed. A production pipeline would normally
push the image to a registry and deploy the immutable registry tag. Jenkins also
has access to the host Docker socket in this lab; use an isolated build agent in a
production design.

## Part 1 — Connect and verify the cluster

Run all commands in this guide **inside the AWS sandbox VM**.

```bash
kubectl config current-context
kubectl cluster-info --context kind-session5
kubectl get nodes -o wide
```

Expected result:

- current context is `kind-session5`;
- one node named `session5-control-plane` is `Ready`;
- the node is both the control plane and the worker for this small lab.

## Part 2 — Inspect the deployed application

```bash
kubectl get namespaces
kubectl get all -n session5
kubectl get deployment training-app -n session5
kubectl get pods -n session5 -o wide
kubectl get service training-app -n session5
```

What to point out:

- the **Deployment** keeps the desired state at two replicas;
- the **Pods** are the two running application instances;
- the **Service** gives the changing Pods one stable access point;
- NodePort `30080` is mapped by kind to VM port `8081`.

Test the application from the VM:

```bash
curl http://127.0.0.1:8081/
curl http://127.0.0.1:8081/health
```

The health endpoint should return:

```json
{"status": "ok"}
```

## Part 3 — Demonstrate self-healing

First list the two Pods:

```bash
kubectl get pods -n session5
```

Copy one Pod name, then delete only that Pod:

```bash
kubectl delete pod <PASTE-ONE-POD-NAME> -n session5
kubectl get pods -n session5 -w
```

Press `Ctrl+C` after the replacement Pod becomes `Running` and `1/1` Ready.

Explanation: the Deployment still wants two replicas. When one Pod disappears,
Kubernetes creates a replacement automatically. The deleted Pod name and the new
Pod name are different.

## Part 4 — Demonstrate GitHub-triggered CI/CD

1. Open `app.py` in the GitHub repository.
2. Change only the value of the `message` field, for example:

   ```python
   "message": "Hello from Session 5 Kubernetes",
   ```

3. Commit the change directly to the `main` branch.
4. Open Jenkins and select `session5-kind-cicd`.
5. Allow up to one minute for Git polling to detect the commit.
6. Open the new build and follow **Console Output**.

Point out the two clear pipeline phases in Stage View:

- **CI - Test & Build:** checkout, Python syntax check, three unit tests, test
  reporting, and Docker image build.
- **CD - Deploy to Kubernetes:** load the tested image into kind, apply the
  manifest, wait for rollout, verify application health, and retain deployment
  evidence.

After the build is green, verify the new image and response inside the VM:

```bash
kubectl get deployment training-app -n session5 \
  -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'

curl http://127.0.0.1:8081/
```

The image tag should contain the new Jenkins build number and Git commit. The HTTP
response should contain the changed message.

## Part 5 — Useful troubleshooting commands

```bash
kubectl get pods -n session5
kubectl describe pod <POD-NAME> -n session5
kubectl logs <POD-NAME> -n session5
kubectl get events -n session5 --sort-by=.lastTimestamp
kubectl rollout status deployment/training-app -n session5
kubectl rollout history deployment/training-app -n session5
```

Quick checks on the VM:

```bash
kind get clusters
docker ps
curl http://127.0.0.1:8081/health
```

## What was performed during environment preparation

- Installed checksum-verified `kubectl` and `kind` binaries.
- Created a one-node kind cluster named `session5`.
- Mapped kind NodePort `30080` to VM port `8081`.
- Built and started a password-protected Jenkins container on port `8080`.
- Created the `session5-kind-cicd` job automatically from `Jenkinsfile.kind`.
- Added a beginner Kubernetes manifest with a Namespace, two-replica Deployment,
  health probes, resource controls, non-root security settings, and a NodePort
  Service.
- Verified the complete pipeline, two healthy Pods, public application health,
  and Pod self-healing.
- Restricted browser ports 8080 and 8081 to the instructor's current public IP.

## Instructor reset commands

Rerun the latest successful Jenkins build to return the application to the desired
state. If only the application needs checking, use:

```bash
kubectl rollout status deployment/training-app -n session5
kubectl get deployment,pods,service -n session5 -o wide
curl http://127.0.0.1:8081/health
```
