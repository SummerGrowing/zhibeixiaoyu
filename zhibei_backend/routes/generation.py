import json
from flask import Blueprint, request, Response, stream_with_context, jsonify
from services.prompt_builder import build_prompt_template
from services.ai_service import stream_ai_response, call_ai_sync
from services.kebiao_retriever import get_relevant_kebiao_context
from services.local_generator import generate_local_fragment

generation_bp = Blueprint('generation', __name__)


def _get_kebiao_context_for_prompt(grade, text_type, focuses):
    """Get smart kebiao context formatted for AI system prompt."""
    context = get_relevant_kebiao_context(grade, text_type, focuses)
    if context:
        return '\n\n【以下为《义务教育语文课程标准（2022年版）》相关段落，请作为教学设计的参考依据，确保教学设计符合课标要求。】\n\n' + context
    return ''


@generation_bp.route('/generate-prompt', methods=['POST'])
def generate_prompt():
    """POST /api/generate-prompt

    Body: {
        "grade": "四年级上册",
        "unit": "第一单元·自然之美",
        "lesson": "观潮",
        "textType": "散文",
        "focuses": ["品读语言", "朗读感悟"],
        "otherFocus": "",
        "idea": "",
        "provider": "deepseek",
        "model": "deepseek-chat",
        "stream": true,
        "unitNumber": 1,
        "lessonNumber": 1
    }
    """
    data = request.json or {}
    grade = data.get('grade', '')
    unit = data.get('unit', '')
    lesson = data.get('lesson', '')
    text_type = data.get('textType', '散文')
    focuses = data.get('focuses', [])
    other_focus = data.get('otherFocus', '')
    idea = data.get('idea', '')
    provider = data.get('provider', '')
    model = data.get('model', '')
    should_stream = data.get('stream', True)
    unit_number = data.get('unitNumber')
    lesson_number = data.get('lessonNumber')

    # Build base prompt from template
    base_prompt = build_prompt_template(
        grade, unit, lesson, text_type, focuses, other_focus, idea,
        unit_number=unit_number, lesson_number=lesson_number
    )

    # No AI provider - return local template
    if not provider or not model:
        return jsonify({"prompt": base_prompt, "source": "local"})

    # Get smart kebiao context
    kebiao_context = _get_kebiao_context_for_prompt(grade, text_type, focuses)

    # Build system prompt for prompt generation
    system_prompt = """你是一位专业的AI备课提示语工程师，精通小学语文教学设计和四维知识框架（文本知识、文体知识、学情知识、教学法知识），深入理解《义务教育语文课程标准（2022年版）》。
请根据以下基础提示语，优化生成一份更完整、更专业的教学设计提示语。
要求：
1. 输出必须是一段自包含的提示语文本（以"你是一位..."开头），教师可以直接复制粘贴到任意AI对话中使用。
2. 不要输出任何解释性文字、引导语或结语，只输出提示语本身。
3. 保持提示语的结构：【四维知识框架】→【个性化设计要求】→【教案要求】→【红线要求】。
4. 在基础提示语的基础上，用具体的专业知识填充【教案要求】中的占位符（如【概括课标要求】【主要内容概括】【已有基础】【学习难点】等），使提示语更加具体和可操作。
5. 如果提示语中包含【教材助读系统参考】，应将其中的单元语文要素、课文教学侧重、课后任务等信息自然融入提示语的相关部分，使提示语更具依据性。但需注意：这些材料是参考而非束缚，教师可以融合自己对教材的理解和学生的具体学情进行创造性运用。
6. 确保提示语充分体现新课标理念：核心素养导向（文化自信、语言运用、思维能力、审美创造）、学习任务群设计、真实情境创设、"教—学—评"一致性。
7. 四维知识框架中的学情知识部分，应结合对应学段课标要求提供具体、准确的学情描述。"""

    full_system = system_prompt + kebiao_context

    messages = [
        {"role": "system", "content": full_system},
        {"role": "user", "content": base_prompt}
    ]

    if should_stream:
        def generate():
            for chunk in stream_ai_response(provider, model, messages):
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    else:
        try:
            result = call_ai_sync(provider, model, messages)
            return jsonify({"prompt": result, "source": "ai"})
        except Exception as e:
            return jsonify({"prompt": base_prompt, "source": "local_fallback", "error": str(e)})


@generation_bp.route('/generate-fragment', methods=['POST'])
def generate_fragment():
    """POST /api/generate-fragment

    Body: {
        "prompt": "...",
        "grade": "四年级上册",
        "unit": "第一单元·自然之美",
        "lesson": "观潮",
        "textType": "散文",
        "focuses": ["品读语言"],
        "otherFocus": "",
        "idea": "",
        "provider": "deepseek",
        "model": "deepseek-chat",
        "stream": true,
        "unitNumber": 1,
        "lessonNumber": 1
    }
    """
    data = request.json or {}
    prompt_text = data.get('prompt', '')
    grade = data.get('grade', '')
    unit = data.get('unit', '')
    lesson = data.get('lesson', '')
    text_type = data.get('textType', '散文')
    focuses = data.get('focuses', [])
    other_focus = data.get('otherFocus', '')
    idea = data.get('idea', '')
    provider = data.get('provider', '')
    model = data.get('model', '')
    should_stream = data.get('stream', True)
    unit_number = data.get('unitNumber')
    lesson_number = data.get('lessonNumber')

    # No AI provider - return local template
    if not provider or not model:
        fragment = generate_local_fragment(
            grade, unit, lesson, text_type, focuses, other_focus, idea,
            unit_number=unit_number, lesson_number=lesson_number
        )
        return jsonify({"fragment": fragment, "source": "local"})

    # Get smart kebiao context
    kebiao_context = _get_kebiao_context_for_prompt(grade, text_type, focuses)

    system_prompt = """你是一位有15年教龄的小学语文特级教师，精通《义务教育语文课程标准（2022年版）》，擅长设计高质量的教案。请根据以下提示语，生成一份完整的教案。要求：
1. 严格按照教案结构输出：主题、一、目标确立依据（课标依据/教材分析/学情分析）、二、教学目标内容（ABCD法+布鲁姆六层级）、三、课型、四、课时安排、五、教学重难点、六、教学方法、七、教学过程（主体，需详细展开）、八、作业布置、九、板书设计。
2. 内容详细、专业、可操作。
3. 教学目标采用ABCD法结构（行为条件+行为表现+表现程度），行为动词从布鲁姆认知目标六层级中选择，根据课文类型灵活选择维度，优先保证核心目标达成。
4. 教学过程各环节要具体、可执行，包含教师活动和学生活动的详细描述。
5. 语言规范、符合教师用语习惯，符合对应学段学生认知水平。
6. 教学设计要落实核心素养培养目标（文化自信、语言运用、思维能力、审美创造），创设真实而有意义的学习情境，体现"教—学—评"一致性。
7. 如果输入的提示语中包含【教材助读系统参考】，应将其中的单元语文要素、课文教学侧重、课后任务等信息融入各教学环节，使教学设计有据可依。但需注意这些仅为参考，应结合教学实际灵活运用。
8. 教学设计要体现四维知识框架（文本知识、文体知识、学情知识、教学法知识）的深度融合。"""

    full_system = system_prompt + kebiao_context

    messages = [
        {"role": "system", "content": full_system},
        {"role": "user", "content": prompt_text}
    ]

    if should_stream:
        def generate():
            for chunk in stream_ai_response(provider, model, messages):
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    else:
        try:
            result = call_ai_sync(provider, model, messages)
            return jsonify({"fragment": result, "source": "ai"})
        except Exception as e:
            fragment = generate_local_fragment(
                grade, unit, lesson, text_type, focuses, other_focus, idea,
                unit_number=unit_number, lesson_number=lesson_number
            )
            return jsonify({"fragment": fragment, "source": "local_fallback", "error": str(e)})
