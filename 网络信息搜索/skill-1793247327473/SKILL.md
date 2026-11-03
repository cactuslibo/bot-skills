---
name: 文献下载流程
description: >-
  Use this when the user asks to run the literature download workflow (文献下载流程)
  for a topic: the 文献搜索 bot searches, then the SciHub bot downloads every found
  title.
---
# 文献下载流程

Run these steps strictly in order. Do not skip, reorder, or substitute steps.

## Input
- The research topic / search requirements from the user (keywords, year range, count, etc.). If the topic is missing, ask for it before starting.

## Step 1: Search (文献搜索 bot)
1. Send the user's full search requirements to the 文献搜索 teammate (id 9110107e-e320-4900-bb65-245252e9ff5d) with SendToAgent.
2. Ask it to return a numbered list of ALL matching papers with exact titles (plus DOI and year if available).
3. Wait for its reply. Tell the user how many papers were found.

## Step 2: Download (SciHub bot)
1. Send the complete title list from Step 1, unchanged, to the SciHub teammate (id 8277d4bd-4832-4627-85a6-ac2277123beb) with SendToAgent.
2. Ask it to download every paper and report, per title, success or failure and where the file was saved.
3. Wait for its reply.

## Step 3: Report to the user
- Send the user a list: each title, downloaded or not, and the file location. List failures separately.
