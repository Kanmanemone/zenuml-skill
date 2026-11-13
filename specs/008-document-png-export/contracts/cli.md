# Contract: 문서 전체 PNG 스크립트

```text
node scripts/export-document-png.js <targetFile.md> [outputBase] --layout <single|paginated>
```

- `targetFile`: `.md`/`.markdown`. 없거나 다른 확장자면 종료 코드 1과 이유.
- `outputBase`: 생략 또는 `""`면 `output.directory`(설정, 원본 폴더 기준)/`<원본 이름>`. `.png`로 끝나면 확장자를 뗀다.
- `--layout`: 필수가 아니며 기본 `paginated`(문서 PDF 스크립트와 같음). 다른 값이면 종료 코드 2.
- 성공: 만든 PNG 경로를 한 줄에 하나씩 표준 출력(페이지 순서), 종료 코드 0.
- 실패: 표준 오류에 이유(페이지 번호·크기 포함 가능), 종료 코드 ≠ 0. 부분 결과로 대체 형식을 만들지 않는다.
- 설정: `png.scale`, `output.directory`를 스스로 읽는다(007 공통 로더).
- 임시 파일(중간 PDF, 다이어그램 SVG, HTML)은 끝나면 지운다.

`export-document-pdf.js`의 인자·출력·동작은 바뀌지 않는다.
