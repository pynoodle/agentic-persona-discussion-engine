# 📊 FusionView 데이터 수집 방법론 요약

## 생성일시
2025-10-20 22:30:00

---

## 🎯 수집 목표
**iPhone 17**과 **Galaxy Z 플립/폴드7**에 대한 실제 사용자 반응 데이터 수집
- YouTube 댓글 분석을 통한 실제 사용자 의견 수집
- 영상 콘텐츠 분석을 통한 제품 인식 파악
- 다국어 데이터 수집 (한국어 + 영어)

---

## 📡 데이터 소스

### 1. **YouTube 데이터** (주요 소스)
- **플랫폼**: YouTube API v3
- **수집 대상**:
  - 비디오 메타데이터 (제목, 설명, 조회수, 좋아요 등)
  - 댓글 데이터 (작성자, 내용, 좋아요, 작성일 등)
  - 채널 정보 (구독자 수, 영상 수 등)
  - 자막/스크립트 (가능한 경우)

### 2. **Reddit 데이터** (보조 소스)
- **서브레딧**: r/iphone, r/apple, r/samsung, r/galaxyfold 등
- **수집 대상**: 포스트 및 댓글

### 3. **Google Trends** (트렌드 분석)
- 검색어 트렌드 분석
- 지역별 관심도 비교

---

## 🔍 검색 키워드 전략

### **iPhone 17 키워드 (20개 핵심 키워드)**
```python
KEYWORDS = [
    # 기본 키워드
    '아이폰 17',
    'iPhone 17',
    
    # 언박싱/리뷰
    '아이폰 17 언박싱',
    'iPhone 17 unboxing',
    '아이폰 17 리뷰',
    'iPhone 17 review',
    
    # 모델별
    '아이폰 17 프로',
    'iPhone 17 Pro',
    '아이폰 17 프로 맥스',
    'iPhone 17 Pro Max',
    
    # 기능별
    '아이폰 17 카메라',
    'iPhone 17 camera',
    '아이폰 17 배터리',
    'iPhone 17 battery',
    '아이폰 17 성능',
    'iPhone 17 performance',
    
    # 비교/구매
    '아이폰 17 vs',
    'iPhone 17 vs',
    '아이폰 17 구매',
    'iPhone 17 buy',
]
```

### **Galaxy Z 플립/폴드7 키워드 (16개 핵심 키워드)**
```python
KEYWORDS = [
    # 기본 키워드
    '갤럭시 Z 플립 7',
    '갤럭시 Z 폴드 7',
    'Galaxy Z flip 7',
    'Galaxy Z fold 7',
    '갤럭시 Z플립 7',
    '갤럭시 Z폴드 7',
    'Galaxy Z flip7',
    'Galaxy Z fold7',
    
    # 언박싱
    '갤럭시 Z 플립 7 언박싱',
    '갤럭시 Z 폴드 7 언박싱',
    'Galaxy Z flip 7 unboxing',
    'Galaxy Z fold 7 unboxing',
    
    # 리뷰
    '갤럭시 Z 플립 7 리뷰',
    '갤럭시 Z 폴드 7 리뷰',
    'Galaxy Z flip 7 review',
    'Galaxy Z fold 7 review',
]
```

---

## 📊 수집 규모 설정

### **대량 수집 모드** (최종 사용)
```
키워드당 영상: 100개
영상당 댓글: 100개

iPhone 17:
- 키워드: 20개
- 예상 총 영상: 2,000개
- 예상 총 댓글: 200,000개

Galaxy:
- 키워드: 16개
- 예상 총 영상: 1,600개
- 예상 총 댓글: 160,000개
```

### **실제 수집 결과**
```
iPhone 17:
- 실제 댓글: 22,071개
- 실제 비디오: 319개

Galaxy Z 플립/폴드7:
- 실제 댓글: 18,306개
- 실제 비디오: 405개

총계: 40,377개 댓글, 724개 비디오
```

*실제 수집량이 예상보다 적은 이유:*
- 중복 비디오 제거
- 댓글이 없거나 비활성화된 비디오 제외
- API 제한 및 수집 시간 고려
- 관련성 낮은 비디오 필터링

---

## 🔄 데이터 수집 프로세스

### **1단계: YouTube 비디오 검색**
```python
search_videos(youtube, keyword, max_results=100)
```
- **검색 기준**:
  - `order='relevance'` - 관련성 순
  - `type='video'` - 비디오만
  - 모든 카테고리 포함
  - 모든 기간 포함 (날짜 제한 없음)

### **2단계: 비디오 상세 정보 수집**
```python
get_video_details(youtube, video_id)
```
- **수집 항목**:
  - 제목, 설명, 태그
  - 조회수, 좋아요, 싫어요
  - 게시일, 업로드 날짜
  - 채널 정보 (구독자 수, 영상 수)
  - 비디오 길이, 카테고리

### **3단계: 댓글 수집**
```python
get_comments(youtube, video_id, max_results=100)
```
- **댓글 정렬 기준**: `order='relevance'` (관련성 순)
- **수집 항목**:
  - 댓글 텍스트
  - 작성자 정보
  - 좋아요 수
  - 작성일시
  - 대댓글 (있는 경우)

### **4단계: 자막/스크립트 수집** (보조)
```python
extract_subtitles_via_api(video_id)
download_audio_and_extract_transcript(video_id)
```
- **방법 1**: YouTube API 자막 (우선)
- **방법 2**: yt-dlp + Whisper STT (대체)
- **언어**: 한국어 > 영어 > 자동 생성

---

## 🛡️ 수집 최적화 및 제한 사항

### **API 제한 대응**
```python
# 요청 간격 설정
'sleep_interval': 1-3,  # 1-3초 대기
'max_sleep_interval': 5,  # 최대 5초 대기
```

### **에러 처리**
- **HttpError 429**: Too Many Requests → 대기 후 재시도
- **HttpError 403**: API 할당량 초과 → 다음 날 재시도
- **댓글 비활성화**: 스킵
- **비디오 삭제/비공개**: 스킵

### **데이터 품질 관리**
1. **중복 제거**: 
   - 동일 비디오 ID 제거
   - 동일 댓글 텍스트 제거

2. **필터링**:
   - 스팸 댓글 제거
   - 너무 짧은 댓글 제거 (<10자)
   - HTML 태그 제거
   - URL 제거

3. **언어 감지**:
   ```python
   def detect_language(text):
       korean_chars = len([c for c in text if '\uAC00' <= c <= '\uD7A3'])
       total_chars = len([c for c in text if c.isalpha()])
       korean_ratio = korean_chars / total_chars if total_chars > 0 else 0
       return 'ko' if korean_ratio > 0.3 else 'en'
   ```

---

## ⚡ 수집 모드별 비교

### **1. 빠른 수집 (Fast Collection)**
```
목적: 빠른 프로토타입 및 테스트
키워드당 영상: 50개
영상당 댓글: 50개
대기 시간: 1초
예상 소요 시간: 1-2시간
```

### **2. 대량 수집 (Massive Collection)** ✅ 최종 사용
```
목적: 포괄적 데이터 수집
키워드당 영상: 100개
영상당 댓글: 100개
대기 시간: 2-3초
예상 소요 시간: 3-5시간
```

### **3. 지속적 수집 (Continuous Collection)**
```
목적: 정기적 업데이트
주기: 매일/주간
증분 수집: 새로운 데이터만
백업: 자동
```

---

## 🔧 기술 스택

### **데이터 수집**
- `google-api-python-client`: YouTube API
- `yt-dlp`: 오디오/자막 다운로드
- `whisper`: 음성-텍스트 변환 (STT)
- `praw`: Reddit API

### **데이터 처리**
- `pandas`: 데이터 조작
- `json`: 데이터 저장
- `xml.etree.ElementTree`: 자막 파싱

### **병렬 처리**
- `concurrent.futures`: 멀티스레딩
- `threading`: 동시 수집

### **스케줄링**
- `schedule`: 정기 수집
- `datetime`: 시간 관리

---

## 📁 데이터 저장 구조

### **파일 구조**
```
data/
├── youtube_raw_data_hybrid.json          # 원시 YouTube 데이터
├── combined_sentiment_analysis_*.json    # 감성 분석 결과
├── precise_conversion_scores_*.json      # 전환 의도 분석
├── improved_dynamic_topic_analysis_*.json # 토픽 분석
└── backups/                              # 백업 폴더
    └── YYYYMMDD_HHMMSS_*.json
```

### **데이터 구조**
```json
{
  "video_id": "...",
  "title": "...",
  "channel_title": "...",
  "view_count": 12345,
  "like_count": 678,
  "comment_count": 90,
  "published_at": "2025-09-20T10:00:00Z",
  "comments": [
    {
      "text": "...",
      "author": "...",
      "like_count": 10,
      "published_at": "...",
      "language": "ko"
    }
  ]
}
```

---

## 📈 수집 품질 지표

### **수집 완성도**
```
iPhone 17:
- 비디오 수집률: 319/2,000 = 15.95%
- 평균 댓글/비디오: 69.2개

Galaxy:
- 비디오 수집률: 405/1,600 = 25.31%
- 평균 댓글/비디오: 45.2개
```

### **언어 분포**
```
iPhone:
- 영어: 66.6%
- 한국어: 33.4%

Galaxy:
- 영어: 53.6%
- 한국어: 46.4%
```

### **데이터 품질**
- ✅ 스팸 필터링: 적용
- ✅ 중복 제거: 적용
- ✅ 언어 감지: 자동
- ✅ 감성 분석: GPT-3.5-turbo
- ✅ 전환 의도 스코어링: 0.0~1.0

---

## 🎯 수집 기준 요약

### **비디오 선정 기준**
1. **관련성**: 키워드와의 관련성 (YouTube 알고리즘)
2. **댓글 활성화**: 댓글이 가능한 비디오
3. **접근 가능**: 공개 비디오만
4. **언어**: 한국어 또는 영어 (주로)

### **댓글 선정 기준**
1. **관련성**: 관련성 순으로 정렬된 상위 100개
2. **길이**: 10자 이상
3. **품질**: 스팸이 아닌 실제 사용자 의견
4. **언어**: 감지 가능한 언어

### **제외 기준**
- ❌ 광고성 댓글
- ❌ 스팸/봇 댓글
- ❌ 너무 짧거나 의미 없는 댓글
- ❌ 중복 댓글
- ❌ HTML/URL만 있는 댓글

---

## 🔄 데이터 업데이트 전략

### **증분 수집** (Incremental Collection)
```python
# 마지막 수집 날짜 이후 데이터만
publishedAfter = last_collection_date
```

### **백업 전략**
- 매 수집 전 자동 백업
- 타임스탬프 기반 파일명
- 최대 보관 기간: 30일

### **병합 전략**
```python
# 기존 데이터와 신규 데이터 병합
# 중복 제거 후 결합
merge_and_deduplicate(old_data, new_data)
```

---

## 💡 수집 과정에서의 인사이트

### **1. 언어별 차이**
- **영어 댓글**: 더 긍정적, 기술 중심, 글로벌 관점
- **한국어 댓글**: 더 비판적, 가격 민감, 실사용 중심

### **2. 비디오 유형별 차이**
- **언박싱**: 첫인상, 디자인 중심
- **리뷰**: 실사용 경험, 장단점
- **비교**: 경쟁 제품 대비, 전환 의도

### **3. 채널 특성**
- **대형 채널**: 다수 댓글, 다양한 의견
- **소형 채널**: 소수 댓글, 팬층 중심

### **4. 시간대별 패턴**
- **출시 직후**: 높은 관심, 기대감
- **출시 후 1개월**: 실사용 후기, 냉정한 평가
- **출시 후 3개월**: 안정화, 전환 결정

---

## 🎓 교훈 및 개선 방향

### **성공 요인**
1. ✅ 다양한 키워드로 포괄적 수집
2. ✅ 관련성 순 정렬로 품질 높은 댓글 확보
3. ✅ 다국어 수집으로 글로벌 시각 확보
4. ✅ 자동화된 백업 및 에러 처리

### **개선 필요**
1. 📌 실제 수집량이 예상보다 적음 → 키워드 다양화
2. 📌 시계열 데이터 부족 → 지속적 수집 필요
3. 📌 Reddit/포럼 데이터 부족 → 다양한 소스 추가
4. 📌 영상 콘텐츠 분석 미흡 → 스크립트 분석 강화

### **향후 계획**
- 🔄 정기적 업데이트 (주간/월간)
- 📊 시계열 분석 추가
- 🌐 더 많은 언어 지원
- 🎥 영상 콘텐츠 깊이 분석
- 💬 Reddit, 포럼 데이터 추가

---

**작성일**: 2025-10-20  
**버전**: 1.0  
**작성자**: FusionView Data Collection Team

