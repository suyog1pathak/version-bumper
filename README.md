# NodeJS version bumper for github actions <img src="https://miro.medium.com/max/1000/1*A3EN6RoI9LIVpL7EhIGHzQ.gif" width="30px">


* Version bumper wrote in python3 which will bump up the version in package.json with below format.

`[majorRelease].[minorRelease].[feature].[hotfix/bugfix]`

`e.g 1.1.2.0`

* he version bumping logic stays in the python code only and it is based on the source branch of the pull request. please find the below logic to increase the nth index number in the version string.

`version String == a.b.c.d`

if source branch is | index in version string to increment
------------- |-------------
`release/*` | b
`feature/*` | c
`bugfix/*` | d
`hotfix/*` | d

below is the trigger condition.

```
  pull_request:
    types: ["closed"]
    branches:
      - 'release/*' 
```

All direct commits on the `release/*` branches will not bump up the version in package.json.

***Flow plan*** 

1] Commit to lower branch. \
2] merge to the parent branch. \
3] GitHub action triggered. \
4] python code will bump up the version in `package.json` and push the same on the parent branch (`destination branch in pull request`).



Required Items|
------------- |
Nodejs App github repo with github actions configured | 
github token added in repo/organization secret |

* env vars required.

Env vars          | details | default
------------- |------------- | ----
LOGLEVEL| logger level supported values are INFO,DEBUG,ERROR| INFO
GITHUB_EVENT_PATH | Github payload json file path, this var has been already set by Github actions. default is `./detail.json` so the script will expect the `detail.json` file on the CWD for local testing. | `./detail.json`
**workflow template:**
* main.yml
```
      - uses: actions/checkout@v2
        with:
          persist-credentials: false # otherwise, the token used is the GITHUB_TOKEN, instead of your personal access token.
          fetch-depth: 0 # otherwise, there would be errors pushing refs to the destination repository.

      - name: wget python code
        uses: wei/wget@v1
        env:
          TOKEN: ${{ secrets.TOKEN }}       
        with:
          args: -O main.py https://${TOKEN}@raw.githubusercontent.com/xyz/pqr/versionBumper/main.py

      - name: setup python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9.4' # install the python version needed
          
      - name: execute py script
        env: 
          LOGLEVEL: "INFO"
        run: python3 main.py
        
      - name: Commit files
        run: |
          git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git commit -m "Version Bump Up " -a

      - name: Push changes
        uses: ad-m/github-push-action@master
        with:
          github_token: ${{ secrets.TOKEN }}
          branch: ${{ github.ref }}
```
