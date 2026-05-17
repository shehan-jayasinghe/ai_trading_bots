-- AlterTable
ALTER TABLE "Workflow" ADD COLUMN     "derivApiToken" TEXT,
ADD COLUMN     "derivAppId" TEXT,
ADD COLUMN     "lastTradeResult" JSONB;
