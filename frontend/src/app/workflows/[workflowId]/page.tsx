import { auth } from "@/auth";
import { WorkflowEditorPage } from "@/components/workflow-editor/workflow-editor-page";
import { redirect } from "next/navigation";

type Props = {
  params: Promise<{ workflowId: string }>;
};

export default async function WorkflowEditorRoute({ params }: Props) {
  const session = await auth();
  if (!session?.user) {
    redirect("/login");
  }

  const { workflowId } = await params;

  return (
    <div className="flex h-screen min-h-0 flex-col bg-white">
      <WorkflowEditorPage workflowId={workflowId} />
    </div>
  );
}
