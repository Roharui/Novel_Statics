import argparse
import asyncio

import novel_platform as platform

from typing import Dict, List, Union
from urllib.parse import urlparse
from validators import url
from exception import WrongLinkException

from novel_platform import Result

from itertools import chain

import sys
py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
if py_ver > 37 and sys.platform.startswith('win'):
  asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

PLATFORM: Dict[str, platform.Platform] = {
  "novelpia.com" : platform.Novelpia(),
  "novel.munpia.com": platform.Munpia(),
  "page.kakao.com": platform.Kakaopage()
}

class NovelStatic:
  def __init__(self, __input: str) -> None:
    self.title = None
    self.url = None

    if url(__input):
      self.url = __input
    else:
      self.title = __input

  async def search(self) -> Union[Result, List[Result]]:
    # 이름 일 경우
    if self.title:
      coroutine = await asyncio.gather(*[engin.searchTitle(self.title) for engin in PLATFORM.values()])
      result = await asyncio.gather(*chain(*coroutine))
      return result
    # 링크일 경우
    else:
      host = urlparse(self.url).hostname

      if not host in PLATFORM.keys():
        raise WrongLinkException()
      
      engin: platform.Platform = PLATFORM[host]

      return await engin.searchURL(self.url)

async def main():
  parser = argparse.ArgumentParser(description="소설 통계 프로그램")

  parser.add_argument("input", help="소설 제목 혹은 링크")

  args = parser.parse_args()

  result = await NovelStatic(args.input).search()

  if type(result) == list:
    for i in result: print(i)
  else:
    print(result)
  
if __name__ == '__main__':
  asyncio.run(main())