from sentence_transformers import SentenceTransformer, util
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

def match_users(target_skills, users):
    user_embeddings = []
    user_profiles = []

    for user in users:
        combined_skills = ", ".join(user.get("skills_offered", []))
        embedding = model.encode(combined_skills, convert_to_tensor=True, device=device)
        user_embeddings.append(embedding)
        user_profiles.append(user)

    target_embedding = model.encode(", ".join(target_skills), convert_to_tensor=True, device=device)

    # Ensure everything is on the same device
    user_embeddings = torch.stack(user_embeddings).to(device)
    target_embedding = target_embedding.to(device)

    sim = util.cos_sim(target_embedding, user_embeddings)
    scores = list(zip(user_profiles, sim[0].tolist()))
    return sorted(scores, key=lambda x: x[1], reverse=True)
