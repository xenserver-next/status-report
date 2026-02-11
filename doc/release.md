# Tagging new versions as part of releasing updates
## Creating a tagged version
This is the process of manually tagging a new version that was merged to master.

There are bump tools which help to automate this process, but they are not added yet.

First switch to the master branch and pull the latest merge.

```bash
$ git switch master
$ git pull origin
git log -n1
commit ebbf629460e138fdbc01c4cc29b27c7af067228f (HEAD -> master, origin/master, origin/HEAD)
Merge: 5138f9e 33b6d6e
Author: Your Name <email@cloud.com>
Date:   Thu Feb 22 15:49:23 2024 +0100

    Merge pull request #82 from xenserver-next/update-dump_xapi_rrds

    CA-389135: Fix the off-by-default and hidden direct-fetched VM RRDs
```

Ensure that your commit hash is identical with the latest commit on master
shown in the GitHub web repository.

Get the latest tag:

```bash
$ git tag | sort -n | tail -n1
v2.0.1
```

Tag a new version using an annotated tag (one which is recorded like a git commit):

```bash
$ git_tag=v2.0.2
$ git tag -m "Tag $git_tag" $git_tag
```

Confirm that the tag was created on the correct commit:

```bash
$ git show $git_tag|head -15
tag v2.0.2
Tagger: Your Name <email@cloud.com>
Date:   Thu Feb 22 11:12:46 2024 +0100

Tag v2.0.2

commit ebbf629460e138fdbc01c4cc29b27c7af067228f
Merge: 5138f9e 33b6d6e
Author: Your Name <email@cloud.com>
Date:   Thu Feb 22 15:49:23 2024 +0100

    Merge pull request #82 from xenserver-next/update-dump_xapi_rrds

    CA-389135: Fix the off-by-default and hidden direct-fetched VM RRDs
$ git push --tags
```

Then wait for some time for the new update to be synced to the mirror repo.

## Creating a new release

After tagging a new version, it would also be good for review to create
a new release:

- With it, you can generate and edit the release notes based on the commits in it.
- Reviewers can get a better picture of the changes in the release using the release notes.

Navigate to <https://github.com/xenserver/status-report/tags>:

- Visit the new tag:
  https://github.com/xenserver/status-report/releases/tag/v2.0.2
- Click the button “Create release from tag”
- That forwards you to a new URL:
  https://github.com/xenserver/status-report/releases/new?tag=v2.0.2
- On it:
  - Change “**Previous tag: auto**” to the last release you want to refer to.
  - Click on: “Generate release notes”
- This adds the git commits since the previous tag to the description field.
- In the description field, add new subsections:
  - Code changes to xen-bugtool
  - Test suite updates
  - Documentation updates
- Move the commits to the corresponding subsections.
- Click on “Preview” to switch the description field into preview mode.
- If all looks great, click the “Publish release” button, else
  click on the “Save draft” button and continue later.
