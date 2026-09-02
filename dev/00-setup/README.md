# 00. Setup

[한국어](README.ko.md) | [English](README.md)

This chapter prepares the environment that every later chapter uses: a Python 3.12 project managed by [uv](https://docs.astral.sh/uv/), AWS credentials that can call Amazon Bedrock, and Bedrock model access in `us-west-2`.

An AWS account is required for the workshop. There are two ways to get a working environment, and you only need one of them. Path A runs the labs on your own machine and is the shorter route if you are reading this repository on GitHub. Path B deploys an AWS-hosted VS Code Server with CloudFormation and is what the instructor-led workshop uses.

![Getting started](../../docs/images/1-getting-start.svg)

> [!NOTE]
> **How the labs work**
> Every later chapter has a `labs/` folder and a `completed/` folder. You type the code into the (empty) file in `labs/` yourself, and `completed/` holds the reference answer to compare against or to run directly if you get stuck. This chapter has no labs: it only holds the setup scripts and the dependency definition.

**Which path to choose**

| Path | Use it when | Time |
|---|---|---|
| [Path A: your own machine](#path-a-your-own-machine) | You want to run the labs on your laptop or any machine you already have | ~10 minutes |
| [Path B: AWS-hosted VS Code Server](#path-b-aws-hosted-vs-code-server) | You are in an instructor-led workshop, or you want a disposable cloud environment with everything preinstalled | ~30 minutes, most of it waiting for CloudFormation |

**What you will learn**

- How to install the workshop Python environment with `uv` and run a lab file from the repository root
- How to configure AWS credentials and enable Amazon Bedrock model access in `us-west-2`
- What the workshop's `create-uv-env.sh` script does, and when you do not need it
- Which AWS services the workshop touches, and which resources keep billing after a lab ends

**Estimated time:** ~10 minutes for Path A, ~30 minutes for Path B

> [!TIP]
> If you use a modern browser you will have no trouble, but the workshop screenshots and the code-server UI are verified against **Mozilla Firefox** and **Google Chrome**.

## Files in this chapter

| File | Purpose |
|---|---|
| `pyproject.toml` | the uv project definition: Python `>=3.12` and every dependency the labs need |
| `uv.lock` | pinned resolution of `pyproject.toml`, so `uv sync` installs the exact versions used to build the labs |
| `.python-version` | pins Python `3.12` for uv |
| `create-uv-env.sh` | the workshop setup script, written for the AWS-hosted VS Code Server (Path B) |
| `install_korean_font.sh` | installs Nanum fonts and points matplotlib at them. Optional, Linux-oriented |
| `test_korean_font.py` | draws a chart with Korean labels to check the font setup, and writes `korean_font_test.png` |

## Path A: your own machine

### 1. Prerequisites

- **Python 3.12.** `pyproject.toml` requires `>=3.12` and `.python-version` pins `3.12`. You do not have to install it yourself: uv downloads a matching interpreter if one is not on your machine.
- **uv.** On macOS or Linux:

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  For Windows and other install methods, see the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).
- **An AWS account** with permission to call Amazon Bedrock and to create the resources listed in [Required IAM permissions](#required-iam-permissions).
- **AWS CLI configured** with credentials for that account, with `us-west-2` as the default region.
- **Docker** only for the OTLP labs in [04-observability](../04-observability/README.md). Nothing else in the workshop needs it.

### 2. Configure AWS credentials

```bash
aws configure
```

Set **Default region name** to `us-west-2`. The labs that name a region explicitly use `us-west-2` (for example `05-agent-memory/completed/stm_persistence.py` and `06-agentcore-runtime/completed/deploy_agent.py`), and the ones that do not use whatever your AWS configuration resolves to, so keeping the default at `us-west-2` avoids a mismatch.

Check that the credentials resolve:

```bash
aws sts get-caller-identity
```

### 3. Enable Amazon Bedrock model access

The labs call Anthropic Claude and Amazon Nova models through Amazon Bedrock in `us-west-2`. Model access is off by default in a new account, so enable it in the Bedrock console under **Model access**: [us-west-2 model access page](https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/modelaccess).

These are the model IDs the lab code actually uses:

| Model ID | Used by |
|---|---|
| `us.anthropic.claude-sonnet-4-20250514-v1:0` | `01-single-agent/completed/models.py`, `04-observability/completed/traces_console.py`, `04-observability/completed/traces_otlp.py`, `08-kiro-dev/completed/hanoi_tower.py` |
| `us.anthropic.claude-sonnet-4-6` | `01-single-agent/completed/self_extending.py`, `01-single-agent/completed/self_modifying.py`, `02-multi-agents/completed/agents_as_tools.py`, `02-multi-agents/completed/swarms.py` |
| `us.amazon.nova-pro-v1:0` | `04-observability/completed/metrics_basic.py` |

The `us.` prefix means these are cross-region inference profiles. The console handles enabling access in the profile's destination regions for you.

Other labs create `Agent()` without naming a model and therefore use the Strands Agents SDK default Bedrock model, so enable the Anthropic Claude models in `us-west-2` even for chapters that are not in the table.

You can list what the account can see with:

```bash
aws bedrock list-foundation-models --region us-west-2 --output table --query "modelSummaries[?providerName=='Anthropic'].modelId"
```

> [!NOTE]
> Chapter 01 additionally needs `amazon.titan-embed-text-v2:0` (Titan Text Embeddings V2) for its Bedrock Knowledge Base, and chapters 05 to 07 use Amazon Bedrock AgentCore. Enable model access as those chapters instruct.

### 4. Install the Python environment

```bash
cd 00-setup
uv sync
cd ..
```

`uv sync` reads `pyproject.toml` and `uv.lock`, downloads Python 3.12 if needed, and creates the virtual environment at `00-setup/.venv`. It does not touch anything outside `00-setup`.

> [!TIP]
> You do not need `create-uv-env.sh` on your own machine. That script is written for the workshop's VS Code Server box: it deletes `.venv`, may install uv and Node.js, installs Linux system fonts with `sudo`, and creates symlinks in the parent directory. See [What create-uv-env.sh does](#what-create-uv-envsh-does) if you want the detail.

### 5. Run a lab

From the repository root, point uv at the project in `00-setup`:

```bash
uv run --project 00-setup python 01-single-agent/completed/basic.py
```

If that prints an agent response, the environment and your Bedrock access are both working.

Or activate the environment once and use plain `python` afterwards:

```bash
source 00-setup/.venv/bin/activate
python 01-single-agent/completed/basic.py
```

On Windows the activation script is `00-setup\.venv\Scripts\activate`.

For the notebook-based parts of the workshop, register the environment as a Jupyter kernel:

```bash
uv run --project 00-setup python -m ipykernel install --user --name agentic-ai-101 --display-name "agentic-ai-101 (uv)"
uv run --project 00-setup jupyter lab
```

Useful uv commands while working through the labs, all run from inside `00-setup`:

```bash
uv add <package>       # add a dependency
uv remove <package>    # remove a dependency
uv sync                # reinstall from pyproject.toml and uv.lock
uv pip list            # list what is installed
```

### 6. Optional: Korean fonts for matplotlib

Some labs plot charts with Korean labels. If the labels render as empty boxes, install a Korean font. `install_korean_font.sh` does this:

```bash
cd 00-setup
sh ./install_korean_font.sh
cd ..
```

It installs the Nanum fonts (`apt-get install fonts-nanum` on Debian and Ubuntu, `yum install nanum-fonts-all` on RHEL and CentOS, otherwise it downloads `NanumGothic.ttf` into `~/.fonts`), refreshes the font cache with `fc-cache`, rewrites matplotlib's `matplotlibrc` to prefer `NanumGothic` and set `axes.unicode_minus: False`, clears `~/.cache/matplotlib`, and writes `test_korean_font.py` into the current directory.

```bash
uv run --project 00-setup python 00-setup/test_korean_font.py
```

The script saves `korean_font_test.png`. Open it and check that the Korean labels are readable.

> [!WARNING]
> This script targets Linux. It calls `sudo`, expects `apt-get`, `yum`, or `fc-cache` to exist, and edits files with GNU `sed -i`, which fails on the BSD `sed` shipped with macOS. Skip it on macOS. `koreanize-matplotlib` is already a dependency in `pyproject.toml`, so `import koreanize_matplotlib` in the notebook or script is the portable alternative. Nothing about the agents themselves depends on this step.

## Path B: AWS-hosted VS Code Server

This is the environment the instructor-led workshop uses. A CloudFormation template builds a VS Code Server (code-server) on AWS with the tooling preinstalled, and you work through the labs in the browser.

First get access to an AWS account, either through a Workshop Studio event or with your own account.

<details>
<summary>(Option 1) Starting with a Workshop Event</summary>

Follow this only if you are running the workshop during an AWS event, using the AWS account the event provides.

1. Get the login URL from the event organizer. When you open it, the page below appears. Click the **Email One-Time Password (OTP)** button.

   <img src="../docs/images/b1-01-sign-with-email.png" alt="Sign in with email">

2. Enter your email address and click **Send passcode**.

   <img src="../docs/images/b1-02-WSS-email.png" alt="Enter email address" width="1000">

3. In your mailbox, open the "Your one-time passcode" email and copy the passcode. Paste it in, then click **Sign in**.

   <img src="../docs/images/b1-03-WSS-passcode.png" alt="Enter the one-time passcode">

4. Enter the access code the event organizer provided and click **Next**. It is usually prefilled or announced by the facilitator.

   <img src="../docs/images/b1-04-enter-access-code.png" alt="Enter access code">

5. Check **I agree with the Terms and Conditions** and click **Join event**.

   <img src="../docs/images/b1-05-workshop-studio-tc.png" alt="Terms and conditions">

6. Click **Open AWS Console** in the left menu to open the AWS console in a new browser window.

   <img src="../docs/images/b1-06-console_access.png" alt="Open AWS Console">

</details>

<details>
<summary>(Option 2) Starting with a personal account</summary>

**Creating an AWS account**

> [!WARNING]
> If you already have an AWS account you can continue with this guide. If you do not, create one first. See [Create and activate an AWS account](https://repost.aws/knowledge-center/create-and-activate-aws-account).

**Creating an IAM user**

Once you have an AWS account, create an IAM user that can access it. Follow the steps below to create a user with administrator privileges. If you already have an IAM user with administrator privileges, skip this.

1. From the [sign-in page](https://console.aws.amazon.com/), sign in to the [IAM console](https://console.aws.amazon.com/iam/home#/home) as the **root user of your AWS account**, using the account email address and password.
2. In the left sidebar of the IAM console, click **Users**, then click **Add user**.

   ![Create IAM user](../../docs/images/iam-user-01.png)

3. Enter `Administrator` for **User name**.
4. Select the **AWS Management Console access** checkbox and check **I want to create an IAM user**.
5. Select **Custom password** and enter a password.
6. Click **Next**.

   ![Create IAM user](../../docs/images/iam-user-02.png)

7. Select **Attach existing policies directly**, check the **AdministratorAccess** policy, and click **Next**.

   ![Attach AdministratorAccess](../../docs/images/iam-user-03.png)

8. Confirm that the AdministratorAccess managed policy is attached to the Administrator user and click **Create user**.

   ![Review and create](../../docs/images/iam-user-04.png)

9. Once the user is created, copy the **Console sign-in URL**. It has this shape:

   ```text
   https://<your_aws_account_id>.signin.aws.amazon.com/console
   ```

   > [!WARNING]
   > `<your_aws_account_id>` is your AWS account's own ID. Running this workshop as the root user is not recommended. Sign in as the Administrator user instead.

   ![Console sign-in URL](../../docs/images/iam-user-05.png)

10. Sign out of the root user, open the URL you copied, and **sign in as the Administrator user you just created**.

</details>

### 1. Deploy the code-server CloudFormation stack

> [!IMPORTANT]
> The CloudFormation template (`code-server-python.yaml`) is **not in this repository**. It is published as a static asset of the AWS Workshop Studio guide, so download it from the workshop's "Deploying Code Server" page. If you are attending a Workshop Studio event, the stack is usually deployed into your account for you and you can skip to step 2. Otherwise, use [Path A](#path-a-your-own-machine): it needs no template.

With the template downloaded:

1. In the AWS console, go to CloudFormation and click **Create stack** then **With new resources (standard)**.

   <img src="../docs/images/b2-sagemaker-3.png" alt="Create stack with new resources">

2. Click **Upload a template file** and upload the yaml file.

   <img src="../docs/images/b3-sagemaker-4.png" alt="Upload a template file">

3. Enter the stack name:

   ```text
   code-server-python
   ```

   <img src="../docs/images/code-server-1.png" alt="Stack name">

4. Check the box acknowledging that the stack creates IAM resources.
5. Leave everything else at its default, click **Next**, then **Submit**.

> [!NOTE]
> The stack takes about 10 minutes or more to finish.

### 2. Open the environment

1. Go to [CloudFormation](https://us-east-1.console.aws.amazon.com/cloudformation/home) in the AWS console and confirm the `code-server-python` stack is deployed.
2. Open the **Outputs** tab, copy the code-server password, then open the code-server URL from the same tab and paste the password in.

   <img src="../docs/images/code-server-2.png" alt="Stack outputs with URL and password" width="1000">
   <img src="../docs/images/b2-sagemaker-2.png" alt="code-server login" width="1000">

3. You should see this screen.

   <img src="../docs/images/b2-sagemaker-7.png" alt="code-server ready" width="800">

4. Open a terminal.

   ![Open the terminal](../../docs/images/b2-2-terminal.png)

### 3. Create the Python environment

Run these commands in the code-server terminal. uv is installed as part of the setup.

```bash
cd 00-setup
chmod +x ./create-uv-env.sh
./create-uv-env.sh myenv 3.12
cd ..
```

![Running create-uv-env.sh](../../docs/images/codeserver-uv-1.png)
![create-uv-env.sh finished](../../docs/images/codeserver-uv-2.png)

> [!NOTE]
> **Reading line 3**
> The command takes these arguments:
> - file to run: `./create-uv-env.sh`
> - virtual environment name: `myenv`
> - Python version to install into the environment: `3.12`
>
> The version argument matters: the script's own default is `3.11`, but `pyproject.toml` requires `>=3.12`. Always pass `3.12`.

### What create-uv-env.sh does

In order, the script:

1. Deletes any existing `.venv` in the current directory with `rm -rf .venv`.
2. Checks for `uv`, and if it is missing asks interactively whether to install it with `curl -LsSf https://astral.sh/uv/install.sh | sh`. Because it prompts, it cannot run unattended.
3. Runs `uv python pin <version>`, then `uv init` only if no `pyproject.toml` exists (this repository has one, so it is left alone), then `uv add ipykernel jupyter` and `uv sync`.
4. Runs `install_korean_font.sh`, which uses `sudo` to install system fonts.
5. Installs Node.js if it is missing (Homebrew on macOS, NodeSource plus `dnf` on Linux).
6. Registers a Jupyter kernel named after the first argument, displayed as `myenv (UV)`.
7. Prints the Python version, the installed packages, and the registered kernels.
8. Moves up to the parent directory and creates symlinks there for `pyproject.toml`, `.venv`, and `uv.lock`, so that `uv run` also works from the repository root. Any existing non-symlink file with those names is renamed to `<name>.backup` first.

> [!NOTE]
> Step 8 leaves three symlinks at the repository root pointing into `00-setup`, which is what makes a bare `uv run` work from the root. If you would rather not have them, delete them and pass `--project` instead:
>
> ```bash
> rm -f pyproject.toml .venv uv.lock
> uv run --project 00-setup python 01-single-agent/completed/basic.py
> ```
>
> Only run the `rm` at the repository root, where these three names are symlinks and not real files.

## Required IAM permissions

The workshop as a whole calls the following services. Chapter 00 by itself only needs Bedrock read and invoke access.

| Service | What the workshop does with it | Chapters |
|---|---|---|
| Amazon Bedrock | `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`, `bedrock:ListFoundationModels` | all |
| Amazon Bedrock Knowledge Bases | create and query a knowledge base, run ingestion jobs | 01 |
| Amazon S3 | bucket holding the knowledge base source documents | 01 |
| Amazon OpenSearch Serverless | vector collection backing the knowledge base | 01 |
| Amazon Bedrock AgentCore Memory | create memory resources, write and read events | 05 |
| Amazon Bedrock AgentCore Runtime | build, deploy, and invoke a hosted agent | 06 |
| Amazon ECR | repository for the container image AgentCore Runtime deploys | 06 |
| IAM | create the execution roles for the knowledge base and the runtime | 01, 06 |
| Amazon CloudWatch | log groups, metrics, and the GenAI Observability dashboard | 04, 06, 07 |
| AWS X-Ray | traces and CloudWatch Transaction Search | 07 |

The workshop assumes broad permissions, and several steps create IAM roles. In a personal sandbox account the simplest option is to attach **AdministratorAccess** to the user you work as, which is what the personal-account setup above does.

> [!WARNING]
> `AdministratorAccess` is not appropriate for a shared or production account. If you have to run this in one, scope a role down to the services in the table above and work with your account administrator.

## Cost note

Nothing in this chapter creates a billable resource beyond the Path B CloudFormation stack, which runs an EC2-backed code-server environment for as long as the stack exists. Delete the stack when you finish the workshop.

From chapter 01 onward, every lab calls Bedrock models, which is billed per token. Several chapters also create resources that bill for as long as they exist, whether or not you are using them:

| Chapter | Standing resources |
|---|---|
| 01 | Bedrock Knowledge Base, OpenSearch Serverless collection, S3 bucket |
| 05 | AgentCore Memory resource |
| 06 | AgentCore Runtime, ECR repository, IAM execution role, CloudWatch log groups |
| 07 | CloudWatch Transaction Search ingestion, trace and log retention |

Each of those chapters has its own **Cleanup** section. Work through them when you are done. An OpenSearch Serverless collection in particular bills continuously.

## Troubleshooting

**`uv: command not found` after installing uv**
The installer puts the binary in `~/.local/bin`. Open a new shell, or add it to `PATH`: `export PATH="$HOME/.local/bin:$PATH"`.

**`AccessDeniedException` when a lab calls a model**
Model access is not enabled for that model ID in `us-west-2`, or your credentials lack `bedrock:InvokeModel`. Check the [model access page](https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/modelaccess) and confirm the model ID in the lab file matches one you enabled.

**`ValidationException` mentioning a region, or the model is not found**
Your default region is not `us-west-2`. Check with `aws configure get region`.

**`ModuleNotFoundError` for `strands` or `bedrock_agentcore`**
You are running the system Python instead of the project environment. Use `uv run --project 00-setup python ...`, or activate `00-setup/.venv` first.

**Korean labels render as boxes in charts**
See [Optional: Korean fonts for matplotlib](#6-optional-korean-fonts-for-matplotlib).

---
Prev: [Agentic AI on AWS Workshop](../README.md) | Next: [01. Building a Basic Single Agent](../01-single-agent/README.md)
