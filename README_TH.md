# STAAD Model Preprocessor

ภาษาอังกฤษ: [README.md](README.md)

โปรแกรมเดสก์ท็อปสำหรับเตรียม ตรวจสอบ และแก้ไข analytical line geometry ก่อนนำไปเปิดใน STAAD.Pro
นำเข้า geometry จาก SketchUp STAAD Prep Bridge หรือไฟล์ DXF ตรวจสอบและซ่อมแซม Node/Member
ตรวจความพร้อมของโมเดล แล้วส่งออกเป็นไฟล์ STAAD `.STD`

> **สถานะปัจจุบัน (2026-09-13):** สร้าง source และแพ็กเกจ Windows portable / SketchUp RBZ รุ่น
> `0.2.0` แล้ว การตรวจแพ็กเกจผ่าน **9/9** และการเปิดโปรแกรมแบบไม่พึ่ง Python ผ่าน **1/1**
> ผู้ใช้ทดสอบ EXE รุ่น `0.2.0` แล้วและรายงานว่าใช้งานได้ดี รุ่นนี้ยังเป็น pre-release ไม่ใช่ stable release
> [PR #1](https://github.com/nariiiiiiiiiiii/STAAD_Model_Preprocessor/pull/1) ซึ่งนำ source และ license
> เข้าสู่ `main` merge แล้ว
>
> [ดาวน์โหลด portable ZIP](https://github.com/nariiiiiiiiiiii/STAAD_Model_Preprocessor/releases/download/v0.2.0/STAAD_Model_Preprocessor_0.2.0_win64_portable.zip)
> เป็นไฟล์โปรแกรมเพียงรายการเดียวที่อัปโหลดไว้ ไม่ใช่โฟลเดอร์ที่แตกไฟล์หรือ EXE เดี่ยว ZIP นี้สร้างก่อนการเปลี่ยน license
> จึงยังไม่ได้ rebuild หรือแทนที่ด้วยแพ็กเกจที่มี license ใหม่ ดู [บันทึก pre-release รุ่น 0.2.0](docs/RELEASE_NOTES_0.2.0.md)
> และ [หน้า release](https://github.com/nariiiiiiiiiiii/STAAD_Model_Preprocessor/releases/tag/v0.2.0)

## โปรแกรมทำอะไรได้บ้าง

- นำเข้า Neutral JSON จาก SketchUp extension หรือนำเข้าเส้น geometry จาก DXF
- ดู Node และ Member ในหน้าต่าง 3D และ Project Explorer; สร้าง ย้าย แบ่ง รวม หรือลบ entity พร้อม Undo/Redo
- ตรวจ geometry และ connectivity ดูรายการปัญหา และใช้ Quick Fix ที่รองรับทั้งแบบรายการเดียวหรือหลายรายการ
- เปิดและบันทึก Project JSON ในตำแหน่งที่ผู้ใช้เลือก รวมถึงใช้ **Save As** เพื่อเปลี่ยนปลายทาง
- ส่งออกไฟล์ STAAD `.STD` ไปยังตำแหน่งที่เลือก พร้อม validation report ข้างไฟล์ที่ส่งออก
- สร้างแพ็กเกจ Windows x64 แบบ standalone ที่ไม่ต้องติดตั้ง โดยเป็นโฟลเดอร์และ ZIP พร้อม SketchUp `.rbz`

โปรแกรมนี้ใช้เตรียม geometry เท่านั้น **ไม่ได้** วิเคราะห์โครงสร้าง คำนวณน้ำหนักบรรทุก ออกแบบสมาชิก
หรือคำนวณตามมาตรฐานการออกแบบ ควรตรวจและยืนยันโมเดลที่ส่งออกใน STAAD.Pro ก่อนนำไปใช้ทางวิศวกรรม

## ขั้นตอนการทำงาน

```text
SketchUp STAAD Prep Bridge JSON ─┐
                                ├─> นำเข้า -> ตรวจ/แก้ไข -> ตรวจความพร้อม -> ส่งออก .STD -> STAAD.Pro
DXF line geometry ──────────────┘
```

SketchUp bridge ส่งออกเฉพาะ geometry ของ edge ที่มองเห็น ไม่ได้อ่าน solid geometry ทั่วไปใน SketchUp
ให้เป็น structural member และใน workflow รุ่น V1 ยังไม่ได้เปิดใช้ native SDK สำหรับอ่านไฟล์ `.skp` โดยตรง

## รันจาก source (Windows)

ต้องใช้ Windows 64-bit, Python **3.12 ขึ้นไป** และ Git เครื่องปลายทางที่ใช้แพ็กเกจ Windows ไม่จำเป็นต้องติดตั้ง Python

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\scripts\run_dev.ps1
```

หลังติดตั้ง editable package แล้ว สามารถเปิดโปรแกรมด้วยคำสั่งนี้ได้เช่นกัน:

```powershell
.\.venv\Scripts\python.exe -m staadprep.app
```

ข้อมูล runtime, ไฟล์ชั่วคราว cache และ build output สำหรับการพัฒนาเก็บไว้ในโฟลเดอร์ภายในโปรเจกต์ตามที่แอปและสคริปต์กำหนด

## ตรวจสอบการเปลี่ยนแปลง

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check src tests
```

ตรวจชนิดข้อมูลแบบ strict เฉพาะ entry point หลักของ UI ได้ด้วย:

```powershell
.\.venv\Scripts\mypy.exe --strict src/staadprep/ui/main_window.py
```

การทดสอบ UI/VTK บางรายการต้องใช้จอจริงและ OpenGL; หาก offscreen renderer ล้มเหลว ไม่ได้แปลว่าการตรวจโมเดลล้มเหลว
ดูผลตรวจและรายการทดสอบด้วยตนเองที่ยังเหลือใน [handoff](docs/HANDOFF.md)

## สร้างแพ็กเกจ (Windows)

การ build แบบ portable ใช้ Nuitka standalone จึงเป็นโฟลเดอร์โปรแกรม ไม่ใช่ `.exe` ไฟล์เดียว
สร้าง SketchUp extension และ Windows executable ให้ตรง version แล้วประกอบเป็น portable folder/ZIP ด้วยสคริปต์:

```powershell
.\.venv\Scripts\python.exe scripts/build_sketchup_rbz.py
.\scripts\build_windows.ps1 -Python .\.venv\Scripts\python.exe
.\.venv\Scripts\python.exe scripts/assemble_portable.py `
  --standalone-dir build/windows/final/app.dist `
  --rbz build/sketchup/STAAD_Prep_Bridge_0.2.0.rbz `
  --dist-root dist
```

สคริปต์อ่าน version จาก `src/staadprep/version.py`; ตรวจชื่อไฟล์และ version ที่ได้ก่อนแจกจ่าย `build/` และ `dist/`
ถูก ignore โดย Git สำหรับรุ่น candidate `0.2.0` ให้ดาวน์โหลดผ่าน GitHub pre-release เฉพาะ ZIP
อย่า commit ZIP หรือโฟลเดอร์ standalone เข้า Git และอย่าระบุเป็น stable release จนกว่าจะได้รับการยอมรับจากเจ้าของ

## ติดตั้ง SketchUp extension

แพ็กเกจมี `SketchUp_Extension/STAAD_Prep_Bridge_0.2.0.rbz` ติดตั้งใน SketchUp ผ่าน
**Extension Manager → Install Extension** ในหน้าต่าง bridge เลือกโฟลเดอร์ inbox ได้เอง
ส่วน `Data/Inbox/SketchUp/` ใน portable package เป็นเพียงตำแหน่งเริ่มต้น ดู [คู่มือติดตั้ง RBZ](packaging/INSTALL_RBZ.md)

## ข้อมูลและการอัปเดต

ข้อมูลที่แอปจัดการจะอยู่ใน `Data/` ข้าง executable ส่วนไฟล์ที่ผู้ใช้เลือกเปิดหรือบันทึกสามารถอยู่นอกโฟลเดอร์ portable ได้
Project JSON ภายนอกจะไม่ถูกคัดลอกหรือสำรองให้อัตโนมัติเมื่อเปลี่ยน portable app โปรดสำรองไฟล์ด้วยตนเอง
ดู [คู่มืออัปเดต](packaging/UPDATE_MANUAL.md) และ [รายละเอียด portable runtime](packaging/README_PORTABLE.md)

## เอกสารโครงการ

- [ดัชนีและสถานะโครงการ](docs/INDEX.md)
- [Handoff และผลตรวจ release](docs/HANDOFF.md)
- [Task board](docs/TASK_BOARD.md)
- [สถาปัตยกรรม](docs/ARCHITECTURE.md)
- [Workflow](docs/WORKFLOW.md)
- [Risk และ approval gates](docs/RISK_GATES.md)
- [Worktree/file relationship mindmap](docs/WORKTREE_MINDMAP.md)
- [บันทึก pre-release รุ่น 0.2.0](docs/RELEASE_NOTES_0.2.0.md)
- [Manifest รายการไฟล์ที่ย้ายไปเก็บใน DEL](DEL/UNUSED_FILES_MANIFEST.md)

## License

License: PolyForm Noncommercial 1.0.0

ใช้ฟรีสำหรับการใช้งานส่วนตัว การศึกษา การวิจัย และวัตถุประสงค์ที่ไม่ใช่เชิงพาณิชย์เท่านั้น

ห้ามใช้เชิงพาณิชย์ เว้นแต่ได้รับอนุญาตเป็นลายลักษณ์อักษรแยกต่างหากจากผู้ถือลิขสิทธิ์ รวมถึงงานที่มีค่าตอบแทน
งาน freelance/consultancy งานส่งมอบที่ได้รับค่าจ้าง การขายซอฟต์แวร์นี้ หรือการทำผลิตภัณฑ์เชิงพาณิชย์จากซอฟต์แวร์นี้

**ข้อยกเว้นที่มีอยู่ใน license ทางการ:** องค์กรบางประเภท เช่น สถาบันการศึกษาและองค์กรวิจัยสาธารณะ
ได้รับอนุญาตให้ใช้งานโดยไม่ขึ้นกับแหล่งทุนหรือข้อผูกพันจากทุน ดังนั้น license นี้อาจไม่ได้ห้ามงานที่มีทุนหรือค่าตอบแทน
ในองค์กรประเภทดังกล่าวทุกกรณี โปรดอ่านหัวข้อ **Noncommercial Organizations** ใน [LICENSE](LICENSE)

Required Notice: Copyright (c) 2026 nariiiiiiiiii

ดู [LICENSE](LICENSE) สำหรับเงื่อนไขฉบับเต็ม และ [PolyForm Noncommercial 1.0.0 ฉบับทางการ](https://polyformproject.org/licenses/noncommercial/1.0.0/)
