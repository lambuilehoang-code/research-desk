from PyQt6.QtCore import QThread, pyqtSignal
import research_agent as agent

class ResearchWorker(QThread):
    """Run research in background so the window stays responsive."""

    finished = pyqtSignal(dict)
    status = pyqtSignal(str)
    chunk = pyqtSignal(str)

    def __init__(self, question, notebook_id):
        super().__init__()
        self.question = question
        self.notebook_id = notebook_id

    def run(self):
        self.status.emit("Querying NotebookLM...")
        nb_data = agent.query_notebooklm(self.question, self.notebook_id)
        if not nb_data:
            self.finished.emit({"ok": False, "error": "NotebookLM failed"})
            return

        answer = (nb_data.get("answer") or "").strip()
        if not answer:
            self.finished.emit({"ok": False, "error": "NotebookLM returned empty answer"})
            return

        analysis = ""
        for chunk in agent.analyze_with_claude(answer, self.question):
            analysis += chunk
            self.chunk.emit(chunk)

        report_path = agent.save_report(self.question, nb_data, analysis)
        agent.save_message(self.notebook_id, "user", self.question)
        agent.save_message(self.notebook_id, "assistant", analysis)

        refs = nb_data.get("references", [])
        self.finished.emit({
            "ok": True,
            "notebook_answer": answer,
            "analysis": analysis,
            "report_path": report_path,
            "reference_count": len(refs),
            "references": refs,
        })
