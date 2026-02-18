#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voting System - 고급 토론 투표 시스템
- 라운드별 안건 관리
- 1-5점 스케일 투표
- 가중치 적용 (고객 40%, 직원 각 20%)
- 과반수 동의 시스템
- 투표 히스토리 저장
"""

from collections import Counter, defaultdict
from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path

class VotingSystem:
    """고급 토론 투표 시스템"""
    
    def __init__(self):
        """투표 시스템 초기화"""
        # 현재 라운드 정보
        self.current_round = 0
        self.motions = {}  # 라운드별 안건
        self.votes = {}    # 라운드별 투표
        
        # 투표 히스토리
        self.voting_history = []
        
        # 통과 기준 (5점 만점 기준)
        self.threshold = 3.0  # 3.0점 이상이면 통과
        
        # 가중치 설정 (고객 40%, 직원 각 20%)
        self.weights = {
            # 고객 페르소나 (총 70%, 7명이므로 각 10%)
            'Foldable_Enthusiast': 0.10,      # 폴더블매력파
            'Ecosystem_Dilemma': 0.10,        # 생태계딜레마
            'Foldable_Critic': 0.10,          # 폴더블비판자
            'Upgrade_Cycler': 0.10,           # 정기업그레이더
            'Value_Seeker': 0.10,             # 가성비추구자
            'Apple_Ecosystem_Loyal': 0.10,    # Apple생태계충성
            'Design_Fatigue': 0.10,           # 디자인피로
            # 직원 페르소나 (각 10%, 총 30%)
            'Marketer': 0.10,
            'Developer': 0.10,
            'Designer': 0.10,
            # 레거시 호환성 (한글 이름)
            'iPhone→Galaxy전환자': 0.10,
            '갤럭시충성고객': 0.10,
            '기술애호가': 0.10,
            '가격민감고객': 0.10,
            '마케터': 0.10,
            '개발자': 0.10,
            '디자이너': 0.10,
        }
        
        # 히스토리 저장 경로
        self.history_dir = Path(__file__).parent.parent / "data"
        self.history_dir.mkdir(exist_ok=True)
    
    def propose_motion(self, motion_text: str, proposer: str) -> int:
        """
        안건 제시
        
        Args:
            motion_text: 안건 내용
            proposer: 제안자
        
        Returns:
            라운드 번호
        """
        self.current_round += 1
        
        motion = {
            'round': self.current_round,
            'motion': motion_text,
            'proposer': proposer,
            'proposed_at': datetime.now().isoformat(),
            'status': 'pending'  # pending, passed, rejected
        }
        
        self.motions[self.current_round] = motion
        self.votes[self.current_round] = {}
        
        print(f"\n{'='*80}")
        print(f"📋 라운드 {self.current_round} - 새로운 안건")
        print('='*80)
        print(f"\n제안자: {proposer}")
        print(f"안건: {motion_text}")
        print("\n투표 방식: 1-5점 스케일")
        print("  1점: 강력 반대")
        print("  2점: 반대")
        print("  3점: 중립")
        print("  4점: 찬성")
        print("  5점: 강력 찬성")
        print('='*80 + "\n")
        
        return self.current_round
    
    def collect_votes(
        self, 
        agents: List, 
        motion_id: Optional[int] = None
    ) -> Dict[str, Dict]:
        """
        각 에이전트로부터 투표 수집
        
        Args:
            agents: 에이전트 리스트
            motion_id: 안건 번호 (None이면 현재 라운드)
        
        Returns:
            {agent_name: {'score': int, 'reason': str}}
        """
        if motion_id is None:
            motion_id = self.current_round
        
        if motion_id not in self.motions:
            print(f"⚠️ 안건 #{motion_id}를 찾을 수 없습니다.")
            return {}
        
        print(f"🗳️ 라운드 {motion_id} 투표 진행 중...\n")
        
        votes_collected = {}
        
        for agent in agents:
            agent_name = agent.name
            
            # 에이전트별 투표 요청
            print(f"📊 {agent_name}님의 투표...")
            
            # 실제 AutoGen 환경에서는 에이전트가 자동으로 투표
            # 여기서는 구조만 정의
            # 실제 투표는 토론 중 수집됨
            
        return votes_collected
    
    def cast_vote(
        self, 
        voter: str, 
        score: int, 
        reason: str = "",
        round_id: Optional[int] = None
    ):
        """
        투표하기 (1-5점 스케일)
        
        Args:
            voter: 투표자 이름
            score: 점수 (1-5)
            reason: 투표 이유
            round_id: 라운드 번호 (None이면 현재)
        """
        if round_id is None:
            round_id = self.current_round
        
        if score < 1 or score > 5:
            print(f"⚠️ 점수는 1-5 사이여야 합니다. (입력: {score})")
            return
        
        if round_id not in self.votes:
            self.votes[round_id] = {}
        
        self.votes[round_id][voter] = {
            'score': score,
            'reason': reason,
            'voted_at': datetime.now().isoformat()
        }
        
        print(f"✅ {voter}: {score}점 투표 완료")
    
    def calculate_result(
        self, 
        votes: Optional[Dict] = None,
        weights: Optional[Dict] = None,
        round_id: Optional[int] = None
    ) -> Dict:
        """
        투표 결과 계산 (가중치 적용)
        
        Args:
            votes: 투표 딕셔너리 {voter: {'score': int, 'reason': str}}
            weights: 가중치 딕셔너리 {voter: weight}
            round_id: 라운드 번호
        
        Returns:
            {
                'weighted_average': float,
                'raw_average': float,
                'passed': bool,
                'vote_details': dict,
                'weights_applied': dict
            }
        """
        if round_id is None:
            round_id = self.current_round
        
        if votes is None:
            votes = self.votes.get(round_id, {})
        
        if weights is None:
            weights = self.weights
        
        if not votes:
            return {
                'weighted_average': 0,
                'raw_average': 0,
                'passed': False,
                'vote_details': {},
                'error': '투표 데이터가 없습니다'
            }
        
        # 가중 평균 계산
        weighted_sum = 0
        total_weight = 0
        raw_sum = 0
        vote_details = {}
        weights_applied = {}
        
        for voter, vote_data in votes.items():
            score = vote_data['score']
            weight = weights.get(voter, 0.1)  # 기본 가중치 0.1
            
            weighted_sum += score * weight
            total_weight += weight
            raw_sum += score
            
            vote_details[voter] = {
                'score': score,
                'weight': weight,
                'weighted_score': score * weight,
                'reason': vote_data.get('reason', '')
            }
            weights_applied[voter] = weight
        
        # 평균 계산
        weighted_average = weighted_sum / total_weight if total_weight > 0 else 0
        raw_average = raw_sum / len(votes) if votes else 0
        
        # 과반수 판정 (가중 평균 3.0 이상 = 통과)
        passed = weighted_average >= 3.0
        
        return {
            'round': round_id,
            'motion': self.motions.get(round_id, {}).get('motion', ''),
            'weighted_average': round(weighted_average, 2),
            'raw_average': round(raw_average, 2),
            'passed': passed,
            'total_voters': len(votes),
            'total_weight': round(total_weight, 2),
            'vote_details': vote_details,
            'weights_applied': weights_applied,
            'threshold': 3.0
        }
    
    def save_voting_history(
        self, 
        filename: Optional[str] = None
    ) -> str:
        """
        투표 히스토리 저장
        
        Args:
            filename: 저장 파일명 (None이면 자동 생성)
        
        Returns:
            저장된 파일 경로
        """
        if filename is None:
            filename = f"voting_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.history_dir / filename
        
        # 히스토리 데이터 구성
        history_data = {
            'saved_at': datetime.now().isoformat(),
            'total_rounds': self.current_round,
            'rounds': []
        }
        
        for round_id in range(1, self.current_round + 1):
            motion = self.motions.get(round_id, {})
            votes = self.votes.get(round_id, {})
            
            if votes:
                result = self.calculate_result(votes, round_id=round_id)
            else:
                result = {'error': '투표 없음'}
            
            round_data = {
                'round': round_id,
                'motion': motion,
                'votes': votes,
                'result': result
            }
            
            history_data['rounds'].append(round_data)
        
        # JSON으로 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 투표 히스토리 저장 완료: {filepath}")
        return str(filepath)
    
    def display_results(self, round_id: Optional[int] = None):
        """
        투표 결과 표시
        
        Args:
            round_id: 라운드 번호 (None이면 현재)
        """
        if round_id is None:
            round_id = self.current_round
        
        result = self.calculate_result(round_id=round_id)
        
        if 'error' in result:
            print(f"❌ {result['error']}")
            return
        
        print("\n" + "="*80)
        print(f"🗳️ 라운드 {result['round']} 투표 결과")
        print("="*80)
        
        print(f"\n📋 안건: {result['motion']}")
        print(f"\n총 투표자: {result['total_voters']}명")
        print(f"총 가중치: {result['total_weight']}")
        
        # 투표 상세 (점수순 정렬)
        print(f"\n📊 투표 상세 (점수순):")
        print("-"*80)
        
        sorted_votes = sorted(
            result['vote_details'].items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        for voter, details in sorted_votes:
            score = details['score']
            weight = details['weight']
            weighted_score = details['weighted_score']
            reason = details['reason']
            
            # 점수 시각화
            bar = "⭐" * score
            
            print(f"\n{voter:20s}: {score}점 {bar}")
            print(f"  가중치: {weight:.0%} | 가중 점수: {weighted_score:.2f}")
            if reason:
                print(f"  이유: {reason}")
        
        # 결과 요약
        print("\n" + "="*80)
        print("📈 결과 요약")
        print("-"*80)
        print(f"  일반 평균: {result['raw_average']:.2f}점 / 5점")
        print(f"  가중 평균: {result['weighted_average']:.2f}점 / 5점")
        print(f"  통과 기준: {result['threshold']:.1f}점 이상")
        print()
        
        if result['passed']:
            print(f"  ✅ 통과! (가중 평균 {result['weighted_average']:.2f}점 ≥ {result['threshold']}점)")
        else:
            print(f"  ❌ 부결 (가중 평균 {result['weighted_average']:.2f}점 < {result['threshold']}점)")
        
        print("="*80)
    
    def get_voting_summary(self) -> Dict:
        """
        전체 투표 요약
        
        Returns:
            전체 라운드 요약 통계
        """
        summary = {
            'total_rounds': self.current_round,
            'passed_motions': 0,
            'rejected_motions': 0,
            'average_score': 0,
            'rounds': []
        }
        
        total_weighted = 0
        count = 0
        
        for round_id in range(1, self.current_round + 1):
            if round_id in self.votes and self.votes[round_id]:
                result = self.calculate_result(round_id=round_id)
                
                if result['passed']:
                    summary['passed_motions'] += 1
                else:
                    summary['rejected_motions'] += 1
                
                total_weighted += result['weighted_average']
                count += 1
                
                summary['rounds'].append({
                    'round': round_id,
                    'motion': result['motion'],
                    'weighted_average': result['weighted_average'],
                    'passed': result['passed']
                })
        
        if count > 0:
            summary['average_score'] = round(total_weighted / count, 2)
        
        return summary
    
    def display_summary(self):
        """전체 투표 요약 표시"""
        summary = self.get_voting_summary()
        
        print("\n" + "="*80)
        print("📊 전체 투표 요약")
        print("="*80)
        
        print(f"\n총 라운드: {summary['total_rounds']}")
        print(f"통과: {summary['passed_motions']}건")
        print(f"부결: {summary['rejected_motions']}건")
        print(f"전체 평균: {summary['average_score']:.2f}점")
        
        if summary['rounds']:
            print(f"\n라운드별 결과:")
            print("-"*80)
            for round_data in summary['rounds']:
                status = "✅ 통과" if round_data['passed'] else "❌ 부결"
                print(f"\nR{round_data['round']}. {round_data['motion'][:50]}...")
                print(f"     평균: {round_data['weighted_average']:.2f}점 | {status}")
        
        print("="*80)
    
    def reset(self):
        """투표 초기화 (새 토론 시작)"""
        # 현재 히스토리 저장
        if self.current_round > 0:
            self.save_voting_history()
        
        # 초기화
        self.current_round = 0
        self.motions = {}
        self.votes = {}

# 테스트 및 사용 예시
if __name__ == "__main__":
    print("🚀 투표 시스템 테스트 시작\n")
    
    # 투표 시스템 초기화
    voting = VotingSystem()
    
    print("="*80)
    print("📊 가중치 설정")
    print("="*80)
    print("\n고객 페르소나 (총 40%):")
    print("  - iPhone→Galaxy전환자: 10%")
    print("  - 갤럭시충성고객: 10%")
    print("  - 기술애호가: 10%")
    print("  - 가격민감고객: 10%")
    print("\n직원 페르소나 (각 20%):")
    print("  - 마케터: 20%")
    print("  - 개발자: 20%")
    print("  - 디자이너: 20%")
    print("="*80)
    
    # 라운드 1: S펜 제거 결정
    print("\n" + "="*80)
    print("🎯 테스트 시나리오: S펜 제거 결정")
    print("="*80)
    
    voting.propose_motion(
        "Galaxy Fold 7에서 S펜 지원을 제거한다",
        "디자이너"
    )
    
    # 투표 수집 (1-5점 스케일)
    print("📊 투표 수집 중...\n")
    
    voting.cast_vote("마케터", 4, "대중화를 위해 필요. 얇음 선호 88회 언급")
    voting.cast_vote("개발자", 4, "기술적 제약. S펜 넣으면 2mm 두꺼워짐")
    voting.cast_vote("디자이너", 5, "얇은 디자인이 더 중요. 사용자 만족도 높음")
    voting.cast_vote("갤럭시충성고객", 2, "차별화 요소 상실. S펜이 Fold의 정체성")
    voting.cast_vote("iPhone→Galaxy전환자", 4, "얇은 게 더 좋음. 폴더블 매력은 폼팩터")
    voting.cast_vote("기술애호가", 3, "장단점 있음. 시장 반응 봐야")
    voting.cast_vote("가격민감고객", 4, "가격 낮출 수 있으면 찬성")
    
    # 결과 계산 및 표시
    voting.display_results()
    
    # 라운드 2: 가격 전략
    print("\n\n" + "="*80)
    print("🎯 테스트 시나리오 2: 가격 전략")
    print("="*80)
    
    voting.propose_motion(
        "Fold 7 가격을 230만원에서 200만원으로 인하한다",
        "가격민감고객"
    )
    
    voting.cast_vote("마케터", 2, "프리미엄 포지셔닝 상실 우려")
    voting.cast_vote("개발자", 3, "기술 원가 고려 시 어려움")
    voting.cast_vote("디자이너", 3, "브랜드 가치 하락 가능")
    voting.cast_vote("갤럭시충성고객", 4, "가격 낮으면 더 많이 팔릴 듯")
    voting.cast_vote("iPhone→Galaxy전환자", 4, "200만원이면 더 매력적")
    voting.cast_vote("기술애호가", 5, "가성비 좋아짐. 강력 찬성")
    voting.cast_vote("가격민감고객", 5, "당연히 찬성! 비싸서 못 사는 사람 많음")
    
    voting.display_results()
    
    # 전체 요약
    voting.display_summary()
    
    # 히스토리 저장
    saved_file = voting.save_voting_history()
    
    print(f"\n✅ 테스트 완료!")
    print(f"   히스토리: {saved_file}")
