@echo off
chcp 65001 > nul
echo.
echo ========================================
echo   🎭 PersonaBot UI - 개선 버전
echo ========================================
echo.
echo 브라우저가 자동으로 열립니다...
echo URL: http://localhost:8501
echo.
python -m streamlit run app_ui_improved.py
pause


