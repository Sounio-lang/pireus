import Lake
open Lake DSL

-- Standalone PIREUS formal package, introduced after the v1.2.0 extraction.
-- The Sounio monorepo lakefile declares the whole language corpus and, of
-- this tree, only SounioPireusMultiProbePartitionV14 plus its axiom audit.
-- This file declares the PIREUS parity libraries and the Cayley-Dickson
-- cocycle they import. It is not a reconstruction of any lakefile hashed
-- in receipts/, and those historical lakefile_sha256 values do not apply.
-- Toolchain is the monorepo pin leanprover/lean4:v4.33.0. Receipts that
-- record Lean 4.33.1 describe an earlier build, not this package.
package «SounioPireus» where

@[default_target]
lean_lib «SounioPireusAnalyticActionClosure» where

@[default_target]
lean_lib «SounioPireusAnalyticActionClosureAxiomAudit» where

@[default_target]
lean_lib «SounioPireusBasisFixedGaugeRebase» where

@[default_target]
lean_lib «SounioPireusBasisFixedGaugeRebaseAxiomAudit» where

@[default_target]
lean_lib «SounioPireusConcreteQuotientAction» where

@[default_target]
lean_lib «SounioPireusConcreteQuotientActionAxiomAudit» where

@[default_target]
lean_lib «SounioPireusConcreteQuotientTarget03Check» where

@[default_target]
lean_lib «SounioPireusExecutedStreamingProbe» where

@[default_target]
lean_lib «SounioPireusExecutedStreamingProbeAxiomAudit» where

@[default_target]
lean_lib «SounioPireusExecutedStreamingProbeBlocks0» where

@[default_target]
lean_lib «SounioPireusExecutedStreamingProbeBlocks1» where

@[default_target]
lean_lib «SounioPireusExecutedStreamingProbeBlocks2» where

@[default_target]
lean_lib «SounioPireusExecutedStreamingProbeBlocks3» where

@[default_target]
lean_lib «SounioPireusExecutedStreamingProbeBlocks4» where

@[default_target]
lean_lib «SounioPireusExecutedStreamingProbeBlocks5» where

@[default_target]
lean_lib «SounioPireusExecutedStreamingProbeBlocks6» where

@[default_target]
lean_lib «SounioPireusExecutedStreamingProbeBlocks7» where

@[default_target]
lean_lib «SounioPireusExecutedStreamingProbeCertificate» where

@[default_target]
lean_lib «SounioPireusExecutedStreamingProbeCheck» where

@[default_target]
lean_lib «SounioPireusFiniteActionCanonicalization» where

@[default_target]
lean_lib «SounioPireusFiniteActionCanonicalizationAxiomAudit» where

@[default_target]
lean_lib «SounioPireusGL4ActionEnumeration» where

@[default_target]
lean_lib «SounioPireusGL4ActionEnumerationAxiomAudit» where

@[default_target]
lean_lib «SounioPireusGL4AnalyticActionCensus» where

@[default_target]
lean_lib «SounioPireusGL4AnalyticActionCensusAxiomAudit» where

@[default_target]
lean_lib «SounioPireusGL4AnalyticBasisEncoder» where

@[default_target]
lean_lib «SounioPireusGL4AnalyticBasisEncoderAxiomAudit» where

@[default_target]
lean_lib «SounioPireusGL4AnalyticCensus» where

@[default_target]
lean_lib «SounioPireusGL4AnalyticCensusAxiomAudit» where

@[default_target]
lean_lib «SounioPireusGL4AnalyticScanBijection» where

@[default_target]
lean_lib «SounioPireusGL4AnalyticScanBijectionAxiomAudit» where

@[default_target]
lean_lib «SounioPireusGL4AnalyticScanEmbedding» where

@[default_target]
lean_lib «SounioPireusGL4AnalyticScanEmbeddingAxiomAudit» where

@[default_target]
lean_lib «SounioPireusGaugeCoboundaryAction» where

@[default_target]
lean_lib «SounioPireusGaugeCoboundaryActionAxiomAudit» where

@[default_target]
lean_lib «SounioPireusGaugeCoboundaryFaithfulness» where

@[default_target]
lean_lib «SounioPireusGaugeCoboundaryFaithfulnessAxiomAudit» where

@[default_target]
lean_lib «SounioPireusGaugeSectionCanonicalization» where

@[default_target]
lean_lib «SounioPireusGaugeSectionCanonicalizationAxiomAudit» where

@[default_target]
lean_lib «SounioPireusLinearSwapGaugeDescent» where

@[default_target]
lean_lib «SounioPireusLinearSwapGaugeDescentAxiomAudit» where

@[default_target]
lean_lib «SounioPireusMatrixCodeXorEquiv» where

@[default_target]
lean_lib «SounioPireusMatrixCodeXorEquivAxiomAudit» where

@[default_target]
lean_lib «SounioPireusMultiProbePartitionV14» where

@[default_target]
lean_lib «SounioPireusMultiProbePartitionV14AxiomAudit» where

@[default_target]
lean_lib «SounioPireusOperatorDiscoveryEngine» where

@[default_target]
lean_lib «SounioPireusOperatorDiscoveryEngineAxiomAudit» where

@[default_target]
lean_lib «SounioPireusOperatorLoweringForge» where

@[default_target]
lean_lib «SounioPireusOperatorLoweringForgeAxiomAudit» where

@[default_target]
lean_lib «SounioPireusOperatorMorphogenesis» where

@[default_target]
lean_lib «SounioPireusOperatorMorphogenesisAxiomAudit» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedback» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackAtlas» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackAxiomAudit» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackChallenge» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackCore» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackParent» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackParentAction00» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackParentAction01» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackParentAction02» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackParentAction03» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackParentAction04» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackParentAction05» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackParentAction06» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackParentAction07» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackParentAction08» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackParentAction09» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackParentAction10» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackParentAction11» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackShard00» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackShard01» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackShard02» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackShard03» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackShard04» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackShard05» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackShard06» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackShard07» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackShard08» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackShard09» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackShard10» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackShard11» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackShard12» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFeedbackShard13» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFrontier» where

@[default_target]
lean_lib «SounioPireusOperatorNoveltyFrontierAxiomAudit» where

@[default_target]
lean_lib «SounioPireusOperatorOrbitAdmissionReconstruction» where

@[default_target]
lean_lib «SounioPireusOperatorOrbitAdmissionReconstructionAxiomAudit» where

@[default_target]
lean_lib «SounioPireusOperatorOrbitArchiveReconstruction» where

@[default_target]
lean_lib «SounioPireusOperatorOrbitArchiveReconstructionAxiomAudit» where

@[default_target]
lean_lib «SounioPireusOperatorOrbitCanonicalization» where

@[default_target]
lean_lib «SounioPireusOperatorOrbitCanonicalizationAxiomAudit» where

@[default_target]
lean_lib «SounioPireusOperatorOrbitClassReconstruction» where

@[default_target]
lean_lib «SounioPireusOperatorOrbitClassReconstructionAxiomAudit» where

@[default_target]
lean_lib «SounioPireusQuotientNoveltyForge» where

@[default_target]
lean_lib «SounioPireusQuadraticOrbitCertificate» where

@[default_target]
lean_lib «SounioPireusQuadraticOrbitCertificateAxiomAudit» where

@[default_target]
lean_lib «SounioPireusQuadraticNoveltyScalar» where

@[default_target]
lean_lib «SounioPireusQuadraticNoveltyScalarAxiomAudit» where

@[default_target]
lean_lib «SounioPireusQuadraticGroupMoment» where

@[default_target]
lean_lib «SounioPireusQuadraticGroupMomentAxiomAudit» where

@[default_target]
lean_lib «SounioPireusQuadraticGroupMomentConsistency» where

@[default_target]
lean_lib «SounioPireusQuadraticGroupMomentConsistencyAxiomAudit» where

@[default_target]
lean_lib «SounioPireusQuadraticPipeline» where

@[default_target]
lean_lib «SounioPireusQuadraticPipelineAxiomAudit» where

@[default_target]
lean_lib «SounioPireusQuadraticPhaseToCode» where

@[default_target]
lean_lib «SounioPireusQuadraticPhaseToCodeAxiomAudit» where

@[default_target]
lean_lib «SounioPireusAdmissionReward» where

@[default_target]
lean_lib «SounioPireusAdmissionRewardAxiomAudit» where

@[default_target]
lean_lib «SounioPireusSignTableBitVecLex» where

@[default_target]
lean_lib «SounioPireusSignTableBitVecLexAxiomAudit» where

@[default_target]
lean_lib «SounioPireusStreamingMinimumCorrespondence» where

@[default_target]
lean_lib «SounioPireusStreamingMinimumCorrespondenceAxiomAudit» where

@[default_target]
lean_lib «SounioPireusStreamingMinimumCorrespondenceCheck» where

@[default_target]
lean_lib «SounioCDCocycle» where
