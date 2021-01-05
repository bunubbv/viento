![VientoEngine](https://user-images.githubusercontent.com/65072459/103525598-cfb06d00-4ec2-11eb-9b06-192e05fb2096.png)

<img src="https://img.shields.io/pypi/pyversions/Sanic"/> <img src="https://img.shields.io/badge/license-BSD%203--Clause-informational"/>
## VientoEngine
VientoEngine은 Python 기반의 [오픈나무](https://github.com/2du/openNAMU)와 호환되는 '빠르고, 비동기적인' 나무마크 지원 위키 엔진입니다.

Sanic과 aiosqlite를 사용하며, 오픈나무 3.2.0 버전과 호환됩니다.

### TOC
 * [시작](#시작)
 * [기여](#기여)
 * [지원](#지원)
 * [라이선스](#라이선스)
 * [오픈나무](#오픈나무)
 * [기타](#기타)

## 시작
VientoEngine은 Python 3 기반 애플리케이션이며, Python 3.6 이상 버전이 동작하는 환경이 필요합니다.

자세한 내용은 [설치 가이드](https://viento.badawiki.site/install_guide.html)를 참조하세요.

## 기여
VientoEngine에는 버그나 여러 문제점이 존재할 수 있습니다. [이슈 트래커](https://github.com/BadaWikiDev/VientoEngine/issues)에 보고하여 완성도를 높이는 데 도움을 줄 수 있습니다. 직접 새로운 기능을 추가하거나, 버그를 고치는 등의 코드 수정도 [Pull requests](https://github.com/BadaWikiDev/VientoEngine/pulls)로 가능합니다.

VientoEngine에는 확장 기능이 존재합니다. 확장 기능 스토어에서 직접 제작한 확장 기능을 공유할 수도 있습니다.

## 지원
 * 문법
     * 나무마크(namumark)
         * py 렌더러 (JS가 싫거나 컴퓨터 성능이 낮을 시 사용, 기본값)
         * JS 렌더러 (컴퓨터 성능이 좋고, 빠른 렌더러를 원할 때 사용)
     * 더마크(themark)
     * ~~미디어위키(MediaWiki)~~ (예정)
     * ~~모니위키(MoniWiki)~~ (예정)
     
 * DB
     * sqlite
     * ~~MySQL~~ (예정)

## 라이선스
VientoEngine은 BSD 3-Clause License 라이선스로 보호받고 있습니다. VientoEngine을 사용할 때는 반드시 라이선스를 준수해야 하며, 위반할 시 법적 조치가 따를 수 있습니다. 포함된 코드는 아래 목록을 참조하시기 바랍니다.

다음과 같은 프로젝트, 코드를 사용했습니다.
 * [openNAMU](https://github.com/2du/openNAMU) - namumark.py
 * [highlightjs](https://highlightjs.org/) -Syntax highlighting
 * [MathJax](https://www.mathjax.org/) - Numerical expression
 * [shortcut.js](http://www.openjs.com/scripts/events/keyboard_shortcuts/) - Keyboard Shortcuts

## 오픈나무
VientoEngine은 [오픈나무](https://github.com/2du/openNAMU)와 호환됩니다. 하지만 아직 완벽하게 호환되지는 않으며, 일부 수정이 필요합니다.

자세한 내용은 [마이그레이션 가이드](https://viento.badawiki.site/change_engine.html)를 참조하세요.

## 기타
 * [공식 사이트](https://viento.badawiki.site)
 * [기여자 목록](https://github.com/BadaWikiDev/VientoEngine/graphs/contributors)
