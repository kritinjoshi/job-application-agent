import os
import docx
from src.integrations.google.docs.docx_editor import DocxEditor

def run_simulation():
    base_dir = '/Users/mrunalshirude/.gemini/antigravity/scratch/job_application_agent'
    in_path = os.path.join(base_dir, 'data', 'base_resume.docx')
    out_path = os.path.join(base_dir, 'data', 'Simulation_Google_TPM_Creative.docx')
    
    # Mock "Creative Force" edits
    # Note the slight "AI drift" in the 'old' string (extra space at end) to test fuzzy matching
    mock_edits = [
        {
            "old": "Spearheading the research and productization of the industry’s first AI-driven surface keyboard and touchpad for AR/VR; managed the transition from high-ambiguity research to stable global deployment. ",
            "new": "Architected the strategic roadmap for Google-scale AI infrastructure initiatives; transitioned high-ambiguity research into stable global AI models, mirroring the lifecycle requirements of Google's TPU and Vertex AI ecosystems."
        },
        {
            "old": "Oversaw design and implementation of ground-truth annotation schemas to train reward models for reinforcement learning, aligning model behaviors with human-centric interaction standards.",
            "new": "Pioneered ground-truth annotation frameworks to optimize Reward Models for Large-Scale RLHF; ensuring AI Infrastructure alignment with human-centric safety standards at Google-scale."
        }
    ]
    
    print(f"Starting Simulation: 'Creative Force' Resume Transformation (Mock AI Response)")
    print(f"Targeting: Principal TPM, AI Infrastructure @ Google")
    
    if not os.path.exists(in_path):
        print(f"Error: {in_path} not found.")
        return
        
    result_path = DocxEditor.apply_edits(in_path, out_path, mock_edits)
    
    print(f"\nSimulation Complete!")
    print(f"Output saved to: {result_path}")
    print(f"Verification: Check the file for TWO yellow-highlighted, strategically re-imagined bullets.")

if __name__ == "__main__":
    run_simulation()
