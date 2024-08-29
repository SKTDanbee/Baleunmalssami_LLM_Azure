import openai
import faiss
import os

# from dotenv import load_dotenv
from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings # Now this import should work

from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


# openai.api_key = os.getenv('API_KEY')
openai.api_key = ''
user_agent = ''
print(openai.api_key)

# 파일 로드 함수
def load_file(file_name):
    try:
        if file_name.endswith('.txt'):
            loader = TextLoader(file_name, encoding='utf-8')  # Ensure correct encoding
        elif file_name.endswith('.pdf'):
            loader = PyPDFLoader(file_name)
        elif file_name.startswith('http://') or file_name.startswith('https://'):
            loader = WebBaseLoader(file_name)
        else:
            raise ValueError(f"Unsupported file type: {file_name}")

        documents = loader.load()
        return documents
    except Exception as e:
        print(f"Error loading {file_name}: {e}")
        return None
    
def split_text(documents, chunk_size=3000, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(documents)

def vectorize_text(splits):
    # 벡터스토어를 생성합니다.
    vectorstore = FAISS.from_documents(documents=splits, embedding=OpenAIEmbeddings(openai_api_key=openai.api_key))

    # 뉴스에 포함되어 있는 정보를 검색하고 생성합니다.
    return vectorstore.as_retriever()

def format_docs(docs):
    # 검색한 문서 결과를 하나의 문단으로 합쳐줍니다.
    return "\n\n".join(doc.page_content for doc in docs)

def kind_report(num=0):

    """
    # 짜야할 promt template
    # 키보드
    1. 대체어 제시 (input 입력 중인 단어 / 문장)
    # 레포트
    1. 부모용 레포트 (사이버 폭력 / 언어습관)
    2. 자녀용 레포트 (언어 습관)
    """
    alter_word = """
    '{input_text}'가 도덕적인 단어라면 텍스트 그대로 출력해주고 아니라면 대체할 수 있는 올바른 단어를 딕셔너리 형식으로 출력해
    * 딕셔너리 형식을 제외한 추가설명 하지마
    """

    cyber_string_template = """
    ### 과도한 신체노출 및 성적행위 정보
    #### 음란 정보 : 남녀(만화, 삽화, 애니메이션, 춘화, 피규어, 리얼돌 등 표현물 포함)의 성기, 음부, 음모, 항문 등 특정 성적 부위의 노출과 해당 부위가 노출된 상태의 성적 행위를 표현하거나 묘사하는 내용은 음란 정보로 판단합니다. 
    #### 선정성 정보 : 음란 정보를 제외한 과도한 신체노출 및 성적행위 정보는 선정성 정보로 판단합니다.
    ### 폭력적이거나 혐오감 등을 유발하는 정보
    #### 폭력 잔혹성 정보 : 사람과 사람의 표현물(만화, 애니메이션 등의 캐릭터)에 대한 육체적 · 정신적 고통 등을 사실적 · 구체적으로 표현하여 다른 이용자에게 잔혹감을 주는 내용은 폭력성 · 잔혹성 정보로 판단합니다.
    #### 혐오성 정보 : 다수의 이용자들이 거부감을 느끼거나 기피할 수 있는 내용은 혐오성 정보로 판단합니다.
    #### 동물 학대 정보 : “동물학대”란 동물을 대상으로 정당한 사유 없이 불필요하거나 피할 수 있는 신체적 고통과 스트레스를 주는 행위 및 굶주림, 질병 등에 대하여 적절한 조치를 게을리하거나 방치하는 행위를 말합니다. 단비는 다음에 해당하는 행위를 촬영한 사진이나 영상물 및 아래의 행위를 묘사한 내용은 동물학대 정보로 판단합니다.
    ### 욕설 ⋅ 비속어 및 증오 발언 
    #### 욕설, 비속어 : 다른 이용자에게 모욕감 또는 불쾌감을 주거나 언어적 폭력으로 느낄수 있는 과도한 표현은 욕설・비속어 정보로 판단합니다.
    #### 증오 발언
    -출신 (국가, 지역 등)
    -인종
    -외양
    -장애 및 질병 유무
    -사회 경제적 상황 및 지위 (직업, 신분 등)
    -종교
    -연령
    -성별
    -성 정체성
    -성적 지향 또는 기타 정체성 요인
    ### 사이버 폭력의 예방
    - 사이버 상에서 의사소통을 할 때에는 상대방의 입장을 생각하고 타인을 험담하거나 헐뜯는 말을 하지 않도록 한다.
    - 언제,어디서든, 누구든지 사이버 폭력의 가해자, 피해자, 방관자과 될 수 있다는 것을 기억한다.
    - 가정에서는 가족 간의 대화를 통해 인터넷 사용에 대한 규칙을 정한다.
    - 학교에서는 사이버 폭력의 위험성과 사이버 상의 지켜야할 예절 등을 교육한다.
    - 사이버 상에서는 개인정보 공개를 최소화하고 주기적으로 비밀번호를 변경한다.
    - 사이버 상에서 타인의 정보를 공유할 때는 반드시 동의를 먼저 구한다.
    - 사이버 상에서 확신을할 수 없는 정보나 남에게 피해가 될 정보는 유포하지 않는다.
    - 사이버 상에서 누군가가 오프라인 만남을 요청할 경우 만나지 않고 보호자에게 알린다.
    ### 사이버 폭력 관련 기관
    - 푸른 코끼리, link : https://www.bepuco.or.kr/, 비고 : 사이버 폭력 솔루션 제공
    - 에듀넷 티-클리어, link : https://www.edunet.net, <사이버폭력 예방·정보윤리교육> 자료를 제공
    - 학생위기상담 종합서비스, link : https://www.wee.go.kr, 비고 : 온라인 고민상담 서비스 제공 (익명, 비밀)
    - 청소년 사이버 상담센터, link : https://www.cyber1388.kr, 비고 : 온라인 고민상담 서비스 제공 (비밀상담, 실시간 채팅 등)
    - 경찰청 사이버 안전국, link : https://www.cyber.go.kr, 비고 : 사이버 범죄 신고·상담 서비스 제공
    - 안전 Dream(아동·여성·장애인 경찰지원센터), link : https://www.safe182.go.kr, 비고 :학교폭력 및 사이버폭력 신고·상담서비스 제공
    - 푸른나무재단,​ link : http://btf.or.kr/, 비고 : 학교폭력 온라인 상담 제공
    ----------
    너는 청소년 사이버 폭력을 담당하는 경찰이야. 발화자가 사이버 폭력 가해를 할 가능성이 있으면 위의 내용을 참고해서 부모님께 작성해줄 레포트를 작성해줘.
    사이버 폭력 피해 의심이 안된다면 아무 내용도 작성하지 마.

    사이버 폭력이 의심된다면 아래 내용을 작성해줘.

    {child_name}의 사이버 폭력 위험도 레포트 / 부모용

    1. 사이버 폭력 의심 여부 / (높음, 중간, 낮음 중 하나) 
    2. 사이버 폭력 의심 행위 / (사이버 폭력을 행한 시간과 발화 내용 / 상황 정리) 
    3. 사이버 폭력 가해 유형 / (자녀에게서 확인 할 수 있는 가해 유형)
    4. 교육 방법 / (초등학생 사이버 폭력 교육 방법 추천,사이버 폭력 관련 기관 추천 )

    위 4가지 내용 중 해당되는 내용이 없다면 빈칸으로 남겨줘.
    json 형식으로 출력해줘.
    """

    habit_string_template_child = '''
    너는 청소년 언어습관을 분석하는 박사야.
    해당 대화에서 발화자의 언어습관을 분석해서 레포트를 작성해줘. 최대한 정확한 내용을 전달하는게 중요해.
    해당 통계 데이터를 기반으로 작성해줘.
    분석 결과는 총 3가지야.

    {child_name}의 언어습관 분석 레포트 / 사용자용

    1. 전반적인 언어 습관 / (설명) 
    2. 비속어 사용 습관 / (비속어를 사용한 실제 시간, 상황, 발화 내용에 기반한 설명) 
    3. 비속어 사용 TOP 3 / (가장 많이 쓴 비속어 3가지에 대한 뜻)
    4. 비속어 대체 문장 추천 / (top 3 단어 및 문장에 대해서 대체할 수 있는 문장 추천)

    위 3가지 내용 중 해당되는 내용이 없다면 빈칸으로 남겨줘.
    json 형식으로 출력해줘.
    '''

#   {child_name}의 언어습관 분석 레포트 / 부모용
    habit_string_template_parents = '''
    ### 사이버 폭력의 예방
    - 사이버 상에서 의사소통을 할 때에는 상대방의 입장을 생각하고 타인을 험담하거나 헐뜯는 말을 하지 않도록 한다.
    - 언제,어디서든, 누구든지 사이버 폭력의 가해자, 피해자, 방관자과 될 수 있다는 것을 기억한다.
    - 가정에서는 가족 간의 대화를 통해 인터넷 사용에 대한 규칙을 정한다.
    - 학교에서는 사이버 폭력의 위험성과 사이버 상의 지켜야할 예절 등을 교육한다.
    - 사이버 상에서는 개인정보 공개를 최소화하고 주기적으로 비밀번호를 변경한다.
    - 사이버 상에서 타인의 정보를 공유할 때는 반드시 동의를 먼저 구한다.
    - 사이버 상에서 확신을할 수 없는 정보나 남에게 피해가 될 정보는 유포하지 않는다.
    - 사이버 상에서 누군가가 오프라인 만남을 요청할 경우 만나지 않고 보호자에게 알린다.
    ### 사이버 폭력 관련 기관
    - 푸른 코끼리, link : https://www.bepuco.or.kr/, 비고 : 사이버 폭력 솔루션 제공
    - 에듀넷 티-클리어, link : https://www.edunet.net, <사이버폭력 예방·정보윤리교육> 자료를 제공
    - 학생위기상담 종합서비스, link : https://www.wee.go.kr, 비고 : 온라인 고민상담 서비스 제공 (익명, 비밀)
    - 청소년 사이버 상담센터, link : https://www.cyber1388.kr, 비고 : 온라인 고민상담 서비스 제공 (비밀상담, 실시간 채팅 등)
    - 경찰청 사이버 안전국, link : https://www.cyber.go.kr, 비고 : 사이버 범죄 신고·상담 서비스 제공
    - 안전 Dream(아동·여성·장애인 경찰지원센터), link : https://www.safe182.go.kr, 비고 :학교폭력 및 사이버폭력 신고·상담서비스 제공
    - 푸른나무재단,​ link : http://btf.or.kr/, 비고 : 학교폭력 온라인 상담 제공
    ------------
    너는 청소년 언어습관을 분석하는 박사야.
    위의 내용을 참고하고, 해당 대화에서 발화자의 언어습관을 분석해서 레포트를 작성해줘. 검사 대상은 초등학생 4-6학년, 레포트 제공 대상은 보호자인걸 고려해서 세세하게 작성해줘.
    분석 결과는 총 3가지야.

    {child_name}의 언어습관 분석 레포트 / 부모용

    1. 전반적인 언어 습관 / (설명 : 부모가 자녀의 언어습관을 확인할 용도)
    2. 비속어 사용 습관 (비속어를 사용한 실제 시간, 상황, 발화 내용에 기반한 설명)
    3. 자녀 언어 습관 교육 방법과 팁 (가해 예방 교육)

    위 3가지 내용 중 해당되는 내용이 없다면 빈칸으로 남겨줘.
    json 형식으로 출력해줘.
    '''
    if num == 0:
        return SystemMessagePromptTemplate.from_template(alter_word)
    elif num == 1:
        return SystemMessagePromptTemplate.from_template(habit_string_template_parents)
    elif num == 2:
        return SystemMessagePromptTemplate.from_template(habit_string_template_child)
    elif num == 3:
        return SystemMessagePromptTemplate.from_template(cyber_string_template)

# Changed this function to accept a filename parameter
def generate_report(file_name,child_id='test_user_id',kind=1):
    cyber_file_list = [file_name]

    # 모든 문서를 저장할 리스트
    all_documents = []

    # 파일 로드
    for file_name in cyber_file_list:
        documents = load_file(file_name)
        if documents:
            all_documents.extend(documents)

    print(all_documents)
    
    if not all_documents:
        print("No documents loaded. Exiting.")
        exit()

    print("Splitting text...")
    splits = split_text(documents=all_documents)
    if not splits:
        print("No text splits created. Exiting.")
        exit()

    print("Vectorizing text...")
    retriever = vectorize_text(splits)

    prompt = hub.pull("rlm/rag-prompt", api_key=openai.api_key)
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0, api_key=openai.api_key)

    # 체인을 생성합니다.
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    human_message_prompt = HumanMessagePromptTemplate.from_template('{child_name}')

    system_message_prompt = kind_report(kind) # 고정 입력 # report 종류 선택 #1 부모 #2아이 #3사이버폭력

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt]) # 1,2 합
    prompt = chat_prompt.format_prompt(child_name=child_id).to_messages()
    
    result = rag_chain.invoke(
        prompt[0].content
    )  #문서에 대한 질의를 입력하고, 답변을 출력합니다.
        

    return result

# Changed this function to accept a filename parameter
def generate_word(txt):
    prompt = hub.pull("rlm/rag-prompt", api_key=openai.api_key)
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0, api_key=openai.api_key)

    human_message_prompt = HumanMessagePromptTemplate.from_template('{input_text}')


    system_message_prompt = kind_report(0) # 고정 입력 # report 종류 선택 #1 부모 #2아이 #3사이버폭력

    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt]) # 1,2 합

    prompt = chat_prompt.format_prompt(input_text=txt).to_messages()

    
    result = llm.invoke(
        prompt[0].content
    )  #문서에 대한 질의를 입력하고, 답변을 출력합니다.
        
    return result

