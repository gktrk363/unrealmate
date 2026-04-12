# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Dockerfile
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════
# UnrealMate Generated Dockerfile
# Optimized for Unreal Engine build environment
FROM ghcr.io/epicgames/unreal-engine:dev-5.4 AS builder

WORKDIR /project

# Copy project files
COPY . .

# Build project
RUN /home/ue4/UnrealEngine/Engine/Build/BatchFiles/RunUAT.sh \
    BuildCookRun \
    -project=/project/*.uproject \
    -noP4 -cook -stage -archive \
    -archivedirectory=/output \
    -package -clientconfig=Shipping \
    -pak -prereqs -nodebuginfo

# Runtime stage
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y libsdl2-2.0-0 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /output /app
WORKDIR /app
ENTRYPOINT ["./ProjectName"]
